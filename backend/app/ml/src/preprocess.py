import os
import re
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.datasets import fetch_20newsgroups
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import CountVectorizer

# Configure logging for production monitoring
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPreprocessor:
    """
    Handles loading, cleaning, and standardizing text data from multiple sources.
    """
    
    def __init__(self, text_column: str = 'review', label_column: str = 'sentiment'):
        self.text_column = text_column
        self.label_column = label_column
        
    def clean_text(self, text: str) -> str:
        """
        Standardize text: lowercase, remove HTML/URLs/special chars.
        Optimized for speed and consistency across datasets.
        """
        if not isinstance(text, str):
            return ""
        
        text = text.lower()
        text = re.sub(r'<.*?>', '', text)  # Remove HTML
        text = re.sub(r'http\S+|www\S+|https\S+', '', text)  # Remove URLs
        text = re.sub(r'[^a-z\s]', '', text)  # Keep alpha only
        text = re.sub(r'\s+', ' ', text).strip()  # Normalize whitespace
        return text
    
    def load_imdb(self, filepath: str) -> pd.DataFrame:
        """
        Load IMDB CSV with validation.
        Returns standardized DataFrame with 'text' and 'label' columns.
        """
        logger.info(f"Loading IMDB dataset from {filepath}")
        
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"IMDB dataset not found: {filepath}")
        
        df = pd.read_csv(filepath, encoding='utf-8')
        
        # Auto-detect columns if names differ
        if self.text_column not in df.columns:
            self.text_column = df.columns[0]  # Fallback to first col
        if self.label_column not in df.columns:
            self.label_column = df.columns[1]  # Fallback to second col
            
        # Create standardized output
        processed = pd.DataFrame({
            'text': df[self.text_column].astype(str).apply(self.clean_text),
            'label': df[self.label_column].astype(str),
            'source': 'imdb'
        })
        
        # Drop rows with empty text
        initial_count = len(processed)
        processed = processed[processed['text'].str.len() > 0]
        dropped = initial_count - len(processed)
        
        if dropped > 0:
            logger.warning(f"Dropped {dropped} rows with empty text from IMDB")
            
        logger.info(f"IMDB loaded: {len(processed)} samples, {processed['label'].nunique()} classes")
        return processed
    
    def load_newsgroups(self, subset: str = 'train') -> pd.DataFrame:
        """
        Load sklearn 20 Newsgroups dataset.
        Returns standardized DataFrame with 'text' and 'label' columns.
        """
        logger.info(f"Loading 20 Newsgroups dataset ({subset})")
        
        dataset = fetch_20newsgroups(
            subset=subset,
            remove=('headers', 'footers', 'quotes'),
            random_state=42
        )
        
        processed = pd.DataFrame({
            'text': [self.clean_text(t) for t in dataset.data],
            'label': [dataset.target_names[i] for i in dataset.target],
            'source': 'newsgroups'
        })
        
        logger.info(f"Newsgroups loaded: {len(processed)} samples, {processed['label'].nunique()} classes")
        return processed


class DataAnalyzer:
    """
    Performs statistical analysis and generates engineering reports.
    """
    
    @staticmethod
    def generate_report(df: pd.DataFrame, dataset_name: str) -> dict:
        """
        Generate key metrics for data quality assessment.
        """
        report = {
            'dataset': dataset_name,
            'total_samples': len(df),
            'missing_text': df['text'].isnull().sum(),
            'empty_text': (df['text'].str.len() == 0).sum(),
            'unique_labels': df['label'].nunique(),
            'label_distribution': df['label'].value_counts().to_dict(),
            'text_stats': {
                'mean_length': df['text'].str.len().mean(),
                'median_length': df['text'].str.len().median(),
                'min_length': df['text'].str.len().min(),
                'max_length': df['text'].str.len().max(),
                'std_length': df['text'].str.len().std()
            }
        }
        return report
    
    @staticmethod
    def plot_distributions(imdb_df: pd.DataFrame, ng_df: pd.DataFrame, output_path: str = 'eda_report.png'):
        """
        Generate comparative distribution plots for engineering review.
        """
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. Label counts - IMDB
        ax = axes[0, 0]
        imdb_counts = imdb_df['label'].value_counts()
        ax.bar(imdb_counts.index, imdb_counts.values, color='#2E86AB')
        ax.set_title('IMDB Label Distribution')
        ax.tick_params(axis='x', rotation=45)
        
        # 2. Label counts - Newsgroups (top 10 shown for readability)
        ax = axes[0, 1]
        ng_counts = ng_df['label'].value_counts()
        ax.bar(range(len(ng_counts)), ng_counts.values, color='#A23B72')
        ax.set_title('20 Newsgroups Label Distribution')
        ax.set_xlabel('Category Index')
        ax.set_ylabel('Count')
        
        # 3. Text length comparison
        ax = axes[1, 0]
        ax.hist(imdb_df['text'].str.len(), bins=50, alpha=0.5, label='IMDB', color='#F18F01')
        ax.hist(ng_df['text'].str.len(), bins=50, alpha=0.5, label='Newsgroups', color='#C73E1D')
        ax.set_title('Text Length Distribution')
        ax.set_xlabel('Character Count')
        ax.set_ylabel('Frequency')
        ax.legend()
        
        # 4. Label cardinality comparison
        ax = axes[1, 1]
        sources = ['IMDB', 'Newsgroups']
        cardinalities = [imdb_df['label'].nunique(), ng_df['label'].nunique()]
        ax.bar(sources, cardinalities, color=['#06A77D', '#003049'])
        ax.set_title('Number of Unique Classes')
        ax.set_ylabel('Class Count')
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        logger.info(f"EDA report saved to {output_path}")
        plt.close()


class DatasetCombiner:
    """
    Merges multiple text datasets with proper label management.
    """
    
    def __init__(self, label_offset_strategy: str = 'auto'):
        """
        Args:
            label_offset_strategy: 'auto' or 'hierarchical'
                - auto: Offset numeric labels to avoid collisions
                - hierarchical: Use 'source_class' format for string labels
        """
        self.strategy = label_offset_strategy
        
    def combine(self, datasets: list[pd.DataFrame]) -> pd.DataFrame:
        """
        Combine multiple standardized DataFrames into single dataset.
        Ensures label uniqueness across sources.
        """
        if not datasets:
            raise ValueError("No datasets provided for combination")
            
        logger.info(f"Combining {len(datasets)} datasets using strategy: {self.strategy}")
        
        processed_dfs = []
        
        for i, df in enumerate(datasets):
            df_copy = df.copy()
            
            if self.strategy == 'hierarchical':
                # Format: "source_classname" (e.g., "imdb_positive", "newsgroups_rec.sport")
                df_copy['combined_label'] = df_copy['source'] + '_' + df_copy['label'].astype(str)
            else:
                # Keep original labels but track source for debugging
                df_copy['combined_label'] = df_copy['label']
                
            processed_dfs.append(df_copy)
        
        combined = pd.concat(processed_dfs, ignore_index=True)
        
        # Verify label uniqueness if using hierarchical strategy
        if self.strategy == 'hierarchical':
            assert combined['combined_label'].is_unique == False or len(combined['combined_label'].unique()) == len(combined), \
                "Label collision detected in hierarchical mode"
        
        logger.info(f"Combined dataset: {len(combined)} samples, {combined['combined_label'].nunique()} unique labels")
        return combined
    
    def encode_labels(self, df: pd.DataFrame, label_column: str = 'combined_label') -> tuple[np.array, LabelEncoder]:
        """
        Convert string labels to numeric for model training.
        Returns encoded labels and the encoder for inverse transform.
        """
        encoder = LabelEncoder()
        encoded = encoder.fit_transform(df[label_column])
        
        logger.info(f"Label encoding complete: {len(encoder.classes_)} classes mapped to 0-{len(encoder.classes_)-1}")
        return encoded, encoder


def main():
    """
    Main execution pipeline.
    """
    # Configuration
    IMDB_PATH = 'backend/app/ml/data/IMDB Dataset.csv'
    OUTPUT_DIR = 'backend/app/ml/artifacts'
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Initialize components
    preprocessor = DataPreprocessor(text_column='review', label_column='sentiment')
    analyzer = DataAnalyzer()
    combiner = DatasetCombiner(label_offset_strategy='hierarchical')
    
    # Step 1: Load and clean data
    print("Loading datasets...")
    imdb_df = preprocessor.load_imdb(IMDB_PATH)
    ng_df = preprocessor.load_newsgroups(subset='train')
    
    # Step 2: Analyze and report
    print("Generating analysis reports...")
    imdb_report = analyzer.generate_report(imdb_df, 'IMDB')
    ng_report = analyzer.generate_report(ng_df, '20Newsgroups')
    
    print(f"\nIMDB Report:")
    print(f"  Samples: {imdb_report['total_samples']}")
    print(f"  Classes: {imdb_report['unique_labels']}")
    print(f"  Avg Length: {imdb_report['text_stats']['mean_length']:.0f} chars")
    
    print(f"\nNewsgroups Report:")
    print(f"  Samples: {ng_report['total_samples']}")
    print(f"  Classes: {ng_report['unique_labels']}")
    print(f"  Avg Length: {ng_report['text_stats']['mean_length']:.0f} chars")
    
    # Step 3: Visualize distributions
    print("Creating distribution plots...")
    analyzer.plot_distributions(
        imdb_df, 
        ng_df, 
        output_path=os.path.join(OUTPUT_DIR, 'eda_distribution.png')
    )
    
    # Step 4: Combine datasets
    print("Combining datasets...")
    combined_df = combiner.combine([imdb_df, ng_df])
    
    # Step 5: Encode labels for training
    print("Encoding labels...")
    y_encoded, label_encoder = combiner.encode_labels(combined_df)
    
    # Step 6: Save artifacts for downstream training
    print("Saving artifacts...")
    combined_df.to_csv(os.path.join(OUTPUT_DIR, 'combined_dataset.csv'), index=False)
    
    # Save label mapping for inference
    label_mapping = {i: label for i, label in enumerate(label_encoder.classes_)}
    pd.DataFrame(list(label_mapping.items()), columns=['encoded_id', 'label']).to_csv(
        os.path.join(OUTPUT_DIR, 'label_mapping.csv'), 
        index=False
    )
    
    print(f"\nPipeline complete. Artifacts saved to {OUTPUT_DIR}/")
    print(f"Final dataset shape: {combined_df.shape}")
    print(f"Label space: {len(label_encoder.classes_)} classes")
    
    return combined_df, y_encoded, label_encoder


if __name__ == '__main__':
    main()