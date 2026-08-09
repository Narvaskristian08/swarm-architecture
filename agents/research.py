"""
Research Agent
Gathers current information from documentation and the web.
"""
from typing import Dict, Any, List, Optional
import logging

from core import BaseAgent, PromptTemplate, ResponseParser

logger = logging.getLogger(__name__)


class ResearchAgent(BaseAgent):
    """
    Research Agent - Retrieves current information and documentation.
    
    Responsibilities:
    1. Search for current documentation
    2. Verify library/framework versions
    3. Extract code examples
    4. Identify potential issues
    5. Summarize findings clearly
    """
    
    def __init__(self):
        super().__init__(
            agent_id="research",
            name="Research",
            description="Gathers current information and documentation"
        )
        self.capabilities = ["web_research", "documentation_search", "version_check"]
        self.web_tool = None
    
    def set_web_tool(self, web_tool):
        """Set the web tool for this agent"""
        self.web_tool = web_tool
    
    def process(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a research task.
        
        Args:
            task: Dictionary containing:
                - type: Task type (research_topic, check_docs, find_examples)
                - topic: What to research
                - context: Optional context
                
        Returns:
            Dictionary containing research findings
        """
        task_type = task.get("type", "research_topic")
        
        if task_type == "research_topic":
            return self._research_topic(task)
        elif task_type == "check_docs":
            return self._check_documentation(task)
        elif task_type == "find_examples":
            return self._find_examples(task)
        elif task_type == "verify_version":
            return self._verify_version(task)
        else:
            return {
                "status": "error",
                "message": f"Unknown task type: {task_type}"
            }
    
    def _research_topic(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Research a general topic"""
        topic = task.get("topic", "")
        context = task.get("context", "")
        
        if not topic:
            return {"status": "error", "message": "No topic provided"}
        
        self.state.update("working", f"Researching: {topic[:50]}...")
        logger.info(f"Researching topic: {topic}")
        
        # Build research prompt
        prompt = self._build_research_prompt(topic, context)
        
        # Query LLM for research synthesis
        system_prompt = PromptTemplate.get_system_prompt("research")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.5)
        
        # Parse findings
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Research complete")
        
        return {
            "status": "success",
            "topic": topic,
            "findings": sections,
            "summary": sections.get("summary", sections.get("intro", "")),
            "raw_response": response
        }
    
    def _check_documentation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Check documentation for a library or framework"""
        library = task.get("library", "")
        specific_topic = task.get("specific_topic", "")
        
        if not library:
            return {"status": "error", "message": "No library specified"}
        
        self.state.update("working", f"Checking docs for {library}")
        
        # Try to fetch documentation if web tool available
        web_content = None
        if self.web_tool:
            result = self.web_tool.run(operation="search_docs", library=library)
            if result.get("status") == "success":
                web_content = result.get("text", "")
        
        # Build prompt
        prompt = f"""Research the documentation for {library}.
        
Topic: {specific_topic if specific_topic else "General overview"}
"""
        
        if web_content:
            prompt += f"\n\nDocumentation content:\n{web_content[:3000]}\n"
        
        prompt += """
Provide:
1. Current version and key features
2. Installation instructions
3. Basic usage examples
4. Common patterns and best practices
5. Important considerations or gotchas
6. Links to official documentation

Format as clear, actionable information."""
        
        system_prompt = PromptTemplate.get_system_prompt("research")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.5)
        
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", f"Documentation research complete for {library}")
        
        return {
            "status": "success",
            "library": library,
            "documentation": sections,
            "has_web_content": web_content is not None,
            "raw_response": response
        }
    
    def _find_examples(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Find code examples for a specific use case"""
        use_case = task.get("use_case", "")
        language = task.get("language", "python")
        
        if not use_case:
            return {"status": "error", "message": "No use case provided"}
        
        self.state.update("working", f"Finding examples for: {use_case}")
        
        prompt = f"""Find and provide code examples for: {use_case}

Language: {language}

Provide:
1. 2-3 different approaches/examples
2. Explanation of each approach
3. Pros and cons of each
4. Recommended approach with justification

Include complete, working code examples with comments."""
        
        system_prompt = PromptTemplate.get_system_prompt("research")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.6)
        
        # Extract code blocks
        code_blocks = ResponseParser.extract_code_blocks(response)
        sections = ResponseParser.extract_sections(response)
        
        self.state.update("done", "Examples found")
        
        return {
            "status": "success",
            "use_case": use_case,
            "language": language,
            "examples": code_blocks,
            "explanations": sections,
            "raw_response": response
        }
    
    def _verify_version(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Verify current version of a library or framework"""
        library = task.get("library", "")
        
        if not library:
            return {"status": "error", "message": "No library specified"}
        
        self.state.update("working", f"Verifying version for {library}")
        
        prompt = f"""What is the current stable version of {library}?

Provide:
1. Current stable version number
2. Release date
3. Key features in this version
4. Any breaking changes from previous versions
5. Recommended installation command

Be concise and accurate."""
        
        system_prompt = PromptTemplate.get_system_prompt("research")
        response = self.query_llm(prompt, system_prompt=system_prompt, temperature=0.3)
        
        self.state.update("done", "Version check complete")
        
        return {
            "status": "success",
            "library": library,
            "version_info": response,
            "raw_response": response
        }
    
    def _build_research_prompt(self, topic: str, context: str = "") -> str:
        """Build a comprehensive research prompt"""
        prompt_parts = [f"Research the following topic: {topic}"]
        
        if context:
            prompt_parts.append(f"\nContext: {context}")
        
        prompt_parts.append("""
Provide a comprehensive research report including:

1. **Summary**: Brief overview of the topic
2. **Key Information**: Important facts and details
3. **Current Best Practices**: Recommended approaches
4. **Common Patterns**: How it's typically implemented
5. **Potential Issues**: Things to watch out for
6. **Examples**: Practical examples if relevant
7. **Resources**: Where to find more information

Focus on current, accurate information. If something is outdated or uncertain, mention it.""")
        
        return "\n".join(prompt_parts)
    
    def research(self, topic: str, context: str = "") -> Dict[str, Any]:
        """Convenience method for quick research"""
        return self.process({
            "type": "research_topic",
            "topic": topic,
            "context": context
        })