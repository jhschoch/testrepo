"""Policy source scraper module for fetching AI governance policies"""

import hashlib
import logging
from datetime import datetime
from typing import Dict, Optional
import requests
from bs4 import BeautifulSoup

# Optional RSS support
try:
    import feedparser
    FEEDPARSER_AVAILABLE = True
except ImportError:
    FEEDPARSER_AVAILABLE = False


class PolicyScraper:
    """Scrapes policy content from various sources"""

    def __init__(self, timeout: int = 30, max_retries: int = 3):
        self.timeout = timeout
        self.max_retries = max_retries
        self.logger = logging.getLogger(__name__)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def scrape(self, url: str, source_type: str = "web") -> Optional[Dict]:
        """
        Scrape content from a policy source

        Args:
            url: URL of the policy source
            source_type: Type of source (web, rss, api)

        Returns:
            Dictionary containing scraped content and metadata
        """
        try:
            if source_type == "rss":
                return self._scrape_rss(url)
            elif source_type == "web":
                return self._scrape_web(url)
            else:
                self.logger.warning(f"Unsupported source type: {source_type}")
                return None

        except Exception as e:
            self.logger.error(f"Error scraping {url}: {str(e)}")
            return None

    def _scrape_web(self, url: str) -> Optional[Dict]:
        """Scrape content from a regular web page"""
        for attempt in range(self.max_retries):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()

                soup = BeautifulSoup(response.content, 'html.parser')

                # Remove script and style elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()

                # Extract text content
                text = soup.get_text(separator=' ', strip=True)

                # Try to extract title
                title = None
                if soup.title:
                    title = soup.title.string
                elif soup.h1:
                    title = soup.h1.get_text(strip=True)

                # Extract meta description if available
                description = None
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    description = meta_desc['content']

                # Calculate content hash
                content_hash = hashlib.sha256(text.encode()).hexdigest()

                return {
                    'url': url,
                    'title': title,
                    'description': description,
                    'content': text,
                    'content_hash': content_hash,
                    'scraped_at': datetime.utcnow().isoformat(),
                    'status_code': response.status_code
                }

            except requests.RequestException as e:
                self.logger.warning(f"Attempt {attempt + 1} failed for {url}: {str(e)}")
                if attempt == self.max_retries - 1:
                    raise

        return None

    def _scrape_rss(self, url: str) -> Optional[Dict]:
        """Scrape content from an RSS feed"""
        if not FEEDPARSER_AVAILABLE:
            self.logger.warning("RSS support not available (feedparser not installed)")
            return None

        try:
            feed = feedparser.parse(url)

            if not feed.entries:
                return None

            # Get the most recent entry
            latest_entry = feed.entries[0]

            title = latest_entry.get('title', '')
            description = latest_entry.get('description', '')
            content = latest_entry.get('content', [{}])[0].get('value', description)
            link = latest_entry.get('link', url)
            published = latest_entry.get('published', datetime.utcnow().isoformat())

            # Calculate content hash
            combined_content = f"{title} {content}"
            content_hash = hashlib.sha256(combined_content.encode()).hexdigest()

            return {
                'url': link,
                'title': title,
                'description': description,
                'content': content,
                'content_hash': content_hash,
                'published_at': published,
                'scraped_at': datetime.utcnow().isoformat()
            }

        except Exception as e:
            self.logger.error(f"Error parsing RSS feed {url}: {str(e)}")
            return None

    def extract_policy_sections(self, content: str) -> Dict[str, str]:
        """
        Extract relevant sections from policy content

        Args:
            content: Full text content

        Returns:
            Dictionary of section headings and content
        """
        sections = {}

        # Common AI policy keywords to look for
        keywords = [
            'artificial intelligence', 'machine learning', 'ai system',
            'algorithm', 'automated decision', 'risk assessment',
            'transparency', 'accountability', 'governance', 'regulation',
            'compliance', 'ethics', 'safety', 'trustworthy ai'
        ]

        # Split content into paragraphs
        paragraphs = content.split('\n')

        relevant_paragraphs = []
        for para in paragraphs:
            para_lower = para.lower()
            if any(keyword in para_lower for keyword in keywords):
                relevant_paragraphs.append(para.strip())

        # Join relevant paragraphs
        if relevant_paragraphs:
            sections['relevant_content'] = ' '.join(relevant_paragraphs)
        else:
            # If no specific matches, return first 2000 characters
            sections['relevant_content'] = content[:2000]

        return sections
