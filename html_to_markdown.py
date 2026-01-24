#!/usr/bin/env python3
"""
HTML to Markdown Converter - Standalone CLI Tool

This script recursively processes HTML files from a website directory,
cleans the content, and converts them to Markdown format.

Usage:
    python html_to_markdown.py
    python html_to_markdown.py --input data/website --output data/markdown
    python html_to_markdown.py --clean --force

Features:
    - Recursive HTML file discovery
    - Removes scripts, styles, navigation, footers
    - Converts to clean Markdown format
    - Preserves directory structure
    - Progress reporting
    - Statistics summary
"""

import argparse
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from bs4 import BeautifulSoup
from markdownify import markdownify as md


class HTMLToMarkdownConverter:
    """Convert HTML website files to clean Markdown"""
    
    UNWANTED_TAGS = [
        'script', 'style', 'nav', 'footer', 'header',
        'aside', 'iframe', 'noscript', 'svg', 'form',
        'button', 'input', 'select', 'textarea'
    ]
    
    UNWANTED_CLASSES = [
        'navigation', 'nav', 'navbar', 'menu', 'sidebar',
        'footer', 'header', 'breadcrumb', 'cookie', 'advertisement',
        'ads', 'social', 'share', 'comment'
    ]
    
    def __init__(
        self,
        input_dir: Path,
        output_dir: Path,
        verbose: bool = True,
        preserve_structure: bool = True,
    ):
        """
        Initialize converter
        
        Args:
            input_dir: Directory containing HTML files
            output_dir: Directory for output Markdown files
            verbose: Print progress messages
            preserve_structure: Keep original directory structure
        """
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.verbose = verbose
        self.preserve_structure = preserve_structure
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'processed': 0,
            'skipped': 0,
            'errors': 0,
        }
    
    def log(self, message: str):
        """Print message if verbose mode is enabled"""
        if self.verbose:
            print(message)
    
    def find_html_files(self) -> List[Path]:
        """
        Recursively find all HTML files in input directory
        
        Returns:
            List of HTML file paths
        """
        html_files = []
        
        # Find .html and .htm files
        html_files.extend(self.input_dir.rglob("*.html"))
        html_files.extend(self.input_dir.rglob("*.htm"))
        
        # Sort for consistent processing order
        html_files = sorted(html_files)
        
        self.log(f"📁 Found {len(html_files)} HTML files in {self.input_dir}")
        return html_files
    
    def clean_html(self, html_content: str) -> BeautifulSoup:
        """
        Clean HTML content by removing unwanted elements
        
        Args:
            html_content: Raw HTML string
            
        Returns:
            Cleaned BeautifulSoup object
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Remove unwanted tags
        for tag_name in self.UNWANTED_TAGS:
            for element in soup.find_all(tag_name):
                element.decompose()
        
        # Remove elements with unwanted classes
        for class_name in self.UNWANTED_CLASSES:
            for element in soup.find_all(class_=lambda c: c and class_name.lower() in str(c).lower()):
                element.decompose()
        
        # Remove HTML comments
        for comment in soup.find_all(string=lambda text: isinstance(text, str) and '<!--' in text):
            comment.extract()
        
        # Remove empty tags
        for tag in soup.find_all():
            if not tag.get_text(strip=True) and not tag.find_all(['img', 'br', 'hr']):
                tag.decompose()
        
        return soup
    
    def extract_metadata(self, soup: BeautifulSoup, file_path: Path) -> Dict[str, str]:
        """
        Extract metadata from HTML
        
        Args:
            soup: BeautifulSoup object
            file_path: Path to HTML file
            
        Returns:
            Dictionary with metadata
        """
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        else:
            # Fallback to first h1
            h1_tag = soup.find('h1')
            if h1_tag:
                metadata['title'] = h1_tag.get_text(strip=True)
            else:
                metadata['title'] = file_path.stem.replace('_', ' ').title()
        
        # Extract meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            metadata['description'] = meta_desc['content']
        
        # Extract keywords
        meta_keywords = soup.find('meta', attrs={'name': 'keywords'})
        if meta_keywords and meta_keywords.get('content'):
            metadata['keywords'] = meta_keywords['content']
        
        return metadata
    
    def extract_main_content(self, soup: BeautifulSoup) -> BeautifulSoup:
        """
        Extract main content area using heuristics
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Main content as BeautifulSoup object
        """
        # Try semantic tags first
        main_content = soup.find('main')
        
        if not main_content:
            main_content = soup.find('article')
        
        if not main_content:
            # Look for common content container classes
            main_content = soup.find('div', class_=lambda c: c and any(
                x in str(c).lower() for x in ['content', 'main', 'body', 'article']
            ))
        
        if not main_content:
            # Find largest div by text content
            divs = soup.find_all('div')
            if divs:
                main_content = max(divs, key=lambda d: len(d.get_text(strip=True)))
        
        # Fallback to body or entire soup
        if not main_content:
            main_content = soup.find('body') or soup
        
        return main_content
    
    def html_to_markdown(self, soup: BeautifulSoup) -> str:
        """
        Convert HTML to Markdown
        
        Args:
            soup: BeautifulSoup object
            
        Returns:
            Markdown formatted text
        """
        # Convert to markdown
        markdown_text = md(
            str(soup),
            heading_style="ATX",        # Use # for headings
            bullets="-",                # Use - for bullets
            code_language="",           # Don't specify code language
            strip=['a'],                # Strip anchor tags but keep text
            escape_asterisks=False,     # Don't escape asterisks
            escape_underscores=False,   # Don't escape underscores
        )
        
        # Clean up excessive whitespace
        markdown_text = re.sub(r'\n{3,}', '\n\n', markdown_text)
        markdown_text = re.sub(r' +', ' ', markdown_text)
        markdown_text = re.sub(r'\t+', ' ', markdown_text)
        
        # Remove lines with only whitespace
        lines = [line.rstrip() for line in markdown_text.split('\n')]
        markdown_text = '\n'.join(lines)
        
        # Remove excessive blank lines at start and end
        markdown_text = markdown_text.strip()
        
        return markdown_text
    
    def create_markdown_header(self, metadata: Dict[str, str], source_file: Path) -> str:
        """
        Create Markdown frontmatter/header
        
        Args:
            metadata: Metadata dictionary
            source_file: Original HTML file path
            
        Returns:
            Markdown frontmatter
        """
        header_lines = ["---"]
        
        if 'title' in metadata:
            header_lines.append(f"title: \"{metadata['title']}\"")
        
        if 'description' in metadata:
            # Escape quotes in description
            desc = metadata['description'].replace('"', '\\"')
            header_lines.append(f"description: \"{desc}\"")
        
        if 'keywords' in metadata:
            header_lines.append(f"keywords: \"{metadata['keywords']}\"")
        
        header_lines.append(f"source: \"{source_file}\"")
        header_lines.append("---\n")
        
        return '\n'.join(header_lines)
    
    def get_output_path(self, input_file: Path) -> Path:
        """
        Calculate output file path
        
        Args:
            input_file: Input HTML file path
            
        Returns:
            Output Markdown file path
        """
        if self.preserve_structure:
            # Keep directory structure relative to input_dir
            relative_path = input_file.relative_to(self.input_dir)
            output_path = self.output_dir / relative_path
        else:
            # Flatten to output directory
            output_path = self.output_dir / input_file.name
        
        # Change extension to .md
        output_path = output_path.with_suffix('.md')
        
        return output_path
    
    def process_file(self, html_file: Path) -> Tuple[bool, str]:
        """
        Process single HTML file
        
        Args:
            html_file: Path to HTML file
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Read HTML file
            with open(html_file, 'r', encoding='utf-8', errors='ignore') as f:
                html_content = f.read()
            
            # Clean HTML
            soup = self.clean_html(html_content)
            
            # Extract metadata
            metadata = self.extract_metadata(soup, html_file)
            
            # Extract main content
            main_content = self.extract_main_content(soup)
            
            # Convert to Markdown
            markdown_text = self.html_to_markdown(main_content)
            
            # Check if content is sufficient
            if len(markdown_text) < 50:
                return False, f"Insufficient content (< 50 chars)"
            
            # Create full Markdown with frontmatter
            full_markdown = self.create_markdown_header(metadata, html_file)
            full_markdown += "\n\n" + markdown_text
            
            # Calculate output path
            output_path = self.get_output_path(html_file)
            
            # Create output directory if needed
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write Markdown file
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(full_markdown)
            
            return True, str(output_path)
        
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def convert_all(self) -> Dict:
        """
        Convert all HTML files to Markdown
        
        Returns:
            Statistics dictionary
        """
        # Find all HTML files
        html_files = self.find_html_files()
        self.stats['total_files'] = len(html_files)
        
        if not html_files:
            self.log("⚠️  No HTML files found!")
            return self.stats
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.log(f"\n🔄 Converting HTML to Markdown...")
        self.log(f"📂 Input:  {self.input_dir}")
        self.log(f"📂 Output: {self.output_dir}")
        self.log(f"{'='*60}\n")
        
        # Process each file
        for i, html_file in enumerate(html_files, 1):
            relative_path = html_file.relative_to(self.input_dir)
            self.log(f"[{i}/{len(html_files)}] Processing: {relative_path}")
            
            success, message = self.process_file(html_file)
            
            if success:
                self.stats['processed'] += 1
                self.log(f"    ✅ Saved to: {message}")
            else:
                if "Insufficient content" in message:
                    self.stats['skipped'] += 1
                    self.log(f"    ⏭️  Skipped: {message}")
                else:
                    self.stats['errors'] += 1
                    self.log(f"    ❌ Failed: {message}")
            
            self.log("")  # Empty line for readability
        
        return self.stats
    
    def print_summary(self):
        """Print conversion statistics summary"""
        print("\n" + "="*60)
        print("📊 Conversion Summary")
        print("="*60)
        print(f"Total HTML files:    {self.stats['total_files']}")
        print(f"✅ Successfully converted: {self.stats['processed']}")
        print(f"⏭️  Skipped (no content):  {self.stats['skipped']}")
        print(f"❌ Errors:              {self.stats['errors']}")
        print("="*60)
        
        if self.stats['processed'] > 0:
            print(f"\n✅ Markdown files saved to: {self.output_dir}")
        else:
            print(f"\n⚠️  No files were converted!")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Convert HTML website files to Markdown format",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert with default settings
  python html_to_markdown.py

  # Specify custom input/output directories
  python html_to_markdown.py --input data/website --output data/markdown

  # Clean output directory before conversion
  python html_to_markdown.py --clean

  # Force overwrite and be quiet
  python html_to_markdown.py --force --quiet

  # Don't preserve directory structure (flatten)
  python html_to_markdown.py --no-preserve-structure
        """
    )
    
    parser.add_argument(
        '--input', '-i',
        type=str,
        default='data/website',
        help='Input directory containing HTML files (default: data/website)'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='data/markdown',
        help='Output directory for Markdown files (default: data/markdown)'
    )
    
    parser.add_argument(
        '--clean', '-c',
        action='store_true',
        help='Clean output directory before conversion'
    )
    
    parser.add_argument(
        '--force', '-f',
        action='store_true',
        help='Force overwrite existing Markdown files'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress progress messages (only show summary)'
    )
    
    parser.add_argument(
        '--no-preserve-structure',
        action='store_true',
        help='Flatten directory structure (save all to output root)'
    )
    
    args = parser.parse_args()
    
    # Convert paths
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    
    # Validate input directory
    if not input_dir.exists():
        print(f"❌ Error: Input directory not found: {input_dir}")
        print(f"\nPlease create the directory or specify a different path with --input")
        return 1
    
    if not input_dir.is_dir():
        print(f"❌ Error: Input path is not a directory: {input_dir}")
        return 1
    
    # Check if output exists and not forcing
    if output_dir.exists() and not args.force and not args.clean:
        print(f"⚠️  Warning: Output directory already exists: {output_dir}")
        response = input("Continue? This may overwrite existing files. (y/N): ")
        if response.lower() != 'y':
            print("❌ Cancelled by user")
            return 0
    
    # Clean output directory if requested
    if args.clean and output_dir.exists():
        print(f"🗑️  Cleaning output directory: {output_dir}")
        shutil.rmtree(output_dir)
        print("✅ Output directory cleaned\n")
    
    # Create converter
    converter = HTMLToMarkdownConverter(
        input_dir=input_dir,
        output_dir=output_dir,
        verbose=not args.quiet,
        preserve_structure=not args.no_preserve_structure,
    )
    
    # Run conversion
    try:
        stats = converter.convert_all()
        converter.print_summary()
        
        # Exit with appropriate code
        if stats['errors'] > 0:
            return 1
        elif stats['processed'] == 0:
            return 1
        else:
            return 0
    
    except KeyboardInterrupt:
        print("\n\n⚠️  Conversion interrupted by user")
        return 130
    
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
