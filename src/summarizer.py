"""AI-powered summarization module for policy updates"""

import logging
import os
from typing import Dict, Optional
from anthropic import Anthropic
from openai import OpenAI


class PolicySummarizer:
    """Generates summaries of policy content using AI models"""

    def __init__(
        self,
        provider: str = "anthropic",
        model: Optional[str] = None,
        max_length: int = 500,
        temperature: float = 0.3
    ):
        """
        Initialize the summarizer

        Args:
            provider: AI provider ("anthropic" or "openai")
            model: Model name (defaults based on provider)
            max_length: Maximum summary length in words
            temperature: Temperature for generation (0.0 - 1.0)
        """
        self.provider = provider.lower()
        self.max_length = max_length
        self.temperature = temperature
        self.logger = logging.getLogger(__name__)

        # Set default models if not specified
        if model:
            self.model = model
        elif self.provider == "anthropic":
            self.model = "claude-3-5-sonnet-20241022"
        elif self.provider == "openai":
            self.model = "gpt-4-turbo"
        else:
            raise ValueError(f"Unsupported provider: {provider}")

        # Initialize the appropriate client
        self._initialize_client()

    def _initialize_client(self):
        """Initialize the AI client based on provider"""
        try:
            if self.provider == "anthropic":
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if not api_key:
                    raise ValueError("ANTHROPIC_API_KEY not found in environment")
                self.client = Anthropic(api_key=api_key)

            elif self.provider == "openai":
                api_key = os.getenv("OPENAI_API_KEY")
                if not api_key:
                    raise ValueError("OPENAI_API_KEY not found in environment")
                self.client = OpenAI(api_key=api_key)

            else:
                raise ValueError(f"Unsupported provider: {self.provider}")

        except Exception as e:
            self.logger.error(f"Error initializing AI client: {str(e)}")
            raise

    def summarize(self, content: str, context: Optional[Dict] = None) -> Optional[str]:
        """
        Generate a summary of policy content

        Args:
            content: Text content to summarize
            context: Optional context (source name, category, etc.)

        Returns:
            Summary text or None if failed
        """
        try:
            # Prepare the prompt
            prompt = self._build_prompt(content, context)

            # Generate summary based on provider
            if self.provider == "anthropic":
                summary = self._summarize_with_anthropic(prompt)
            elif self.provider == "openai":
                summary = self._summarize_with_openai(prompt)
            else:
                return None

            return summary

        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return None

    def _build_prompt(self, content: str, context: Optional[Dict] = None) -> str:
        """Build the summarization prompt"""
        source_name = context.get('source_name', 'Unknown') if context else 'Unknown'
        category = context.get('category', '') if context else ''
        change_type = context.get('change_type', 'new') if context else 'new'

        # Truncate content if too long (keep first 6000 chars)
        if len(content) > 6000:
            content = content[:6000] + "... [content truncated]"

        prompt = f"""You are an AI governance policy analyst. Your task is to summarize policy updates clearly and concisely.

Source: {source_name}
Category: {category}
Change Type: {change_type}

Policy Content:
{content}

Please provide a comprehensive summary that includes:
1. Main topic and scope of the policy
2. Key requirements or recommendations
3. Important deadlines or timelines (if any)
4. Affected stakeholders or sectors
5. Significant changes from previous versions (if this is an update)

Keep the summary under {self.max_length} words. Focus on the most important and actionable information.

Summary:"""

        return prompt

    def _summarize_with_anthropic(self, prompt: str) -> Optional[str]:
        """Generate summary using Anthropic's Claude"""
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1024,
                temperature=self.temperature,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            # Extract the summary from the response
            if response.content and len(response.content) > 0:
                return response.content[0].text.strip()

            return None

        except Exception as e:
            self.logger.error(f"Anthropic API error: {str(e)}")
            return None

    def _summarize_with_openai(self, prompt: str) -> Optional[str]:
        """Generate summary using OpenAI's GPT"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an AI governance policy analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1024,
                temperature=self.temperature
            )

            # Extract the summary from the response
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content.strip()

            return None

        except Exception as e:
            self.logger.error(f"OpenAI API error: {str(e)}")
            return None

    def generate_change_summary(self, change_info: Dict) -> Optional[str]:
        """
        Generate a summary specifically for a detected change

        Args:
            change_info: Dictionary containing change detection information

        Returns:
            Summary text or None if failed
        """
        content = change_info.get('content', {})
        text_content = content.get('content', '')

        if not text_content:
            return None

        context = {
            'source_name': change_info.get('source_name', 'Unknown'),
            'category': content.get('category', ''),
            'change_type': change_info.get('change_type', 'new')
        }

        return self.summarize(text_content, context)

    def generate_digest(self, changes: list) -> Optional[str]:
        """
        Generate a digest of multiple policy changes

        Args:
            changes: List of change information dictionaries

        Returns:
            Digest summary or None if failed
        """
        if not changes:
            return "No policy changes detected."

        # Build a combined summary of all changes
        digest_prompt = f"""You are an AI governance policy analyst. Generate a concise digest of recent AI governance policy updates.

Number of updates: {len(changes)}

Updates:
"""

        for i, change in enumerate(changes, 1):
            source_name = change.get('source_name', 'Unknown')
            change_type = change.get('change_type', 'update')
            title = change.get('content', {}).get('title', 'No title')

            digest_prompt += f"\n{i}. {source_name} ({change_type}): {title}"

        digest_prompt += f"""

Please create a digest summary (under 300 words) that:
1. Highlights the most significant updates
2. Identifies common themes across the updates
3. Notes any urgent or time-sensitive changes
4. Provides a high-level overview of the policy landscape

Digest:"""

        try:
            if self.provider == "anthropic":
                return self._summarize_with_anthropic(digest_prompt)
            elif self.provider == "openai":
                return self._summarize_with_openai(digest_prompt)
        except Exception as e:
            self.logger.error(f"Error generating digest: {str(e)}")
            return None
