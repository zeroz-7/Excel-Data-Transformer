import os
import yaml
import logging
from typing import Any, Dict

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from .custom_tool import excel_data_inspector_tool

logger = logging.getLogger(__name__)

@CrewBase
class CsvOrganiser:
    """CsvOrganiser crew - loads configs from YAML files and creates agents/tasks."""

    agents_config_path: str = os.path.join(os.path.dirname(__file__), "config", "agents.yaml")
    tasks_config_path: str = os.path.join(os.path.dirname(__file__), "config", "tasks.yaml")

    def __init__(self):
        self.agents_config = self._load_yaml(self.agents_config_path) or {}
        self.tasks_config = self._load_yaml(self.tasks_config_path) or {}
        logger.info("CsvOrganiser initialized with agents/tasks configs")

        # 🔎 Debug logging of YAML
        logger.debug(f"Loaded agents config: {self.agents_config}")
        logger.debug(f"Loaded tasks config: {self.tasks_config}")

    def _load_yaml(self, path: str) -> Dict[str, Any]:
        if not os.path.exists(path):
            logger.warning(f"YAML config not found at: {path}")
            return {}
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.exception(f"Failed to load YAML at {path}: {e}")
            return {}

    @agent
    def script_generator(self) -> Agent:
        agent_conf = self.agents_config.get("script_generator", {})
        logger.info(f"🔧 Creating script_generator agent with enhanced JSON inspection")
        return Agent(
            role=agent_conf.get("role", "Data Analyst"),
            goal=agent_conf.get("goal", "Generate scripts from ACTUAL Excel files or return clear errors if files are invalid."),
            backstory=agent_conf.get("backstory", "You work ONLY with actual file data from JSON inspection. You return clear errors when files cannot be processed."),
            verbose=True,
            tools=[excel_data_inspector_tool],
            llm=self._get_llm(),
            max_iter=agent_conf.get("max_iter", 3),
            max_execution_time=600,
            allow_delegation=agent_conf.get("allow_delegation", False),
            output_format=agent_conf.get("output_format"),
            instructions=[
                "FIRST: Call Excel Data Inspector Tool with the EXACT file paths provided",
                "SECOND: Parse JSON response - CHECK THE 'success' FIELD",
                "THIRD: If 'success' is false, return: 'ERROR: [list specific file errors from JSON]'",
                "FOURTH: If 'success' is true, generate script using ACTUAL columns from JSON",
                "FIFTH: NEVER use hypothetical file names like 'sales.xlsx' or 'data.csv'",
                "SIXTH: If instructed columns don't exist in JSON, handle gracefully in script",
                "CRITICAL: Return clear error messages when files cannot be processed"
            ],
        )

    @agent
    def validator(self) -> Agent:
        agent_conf = self.agents_config.get("validator", {})
        logger.info(f"🔧 Creating validator agent with JSON-aware validation")
        return Agent(
            role=agent_conf.get("role", "Reviewer"),
            goal=agent_conf.get("goal", "Check the generated script for accuracy using JSON inspection data."),
            backstory=agent_conf.get("backstory", "You validate correctness of generated scripts against JSON file structures."),
            verbose=True,
            llm=self._get_llm(),
            max_iter=agent_conf.get("max_iter", 2),
            max_execution_time=600,
            allow_delegation=agent_conf.get("allow_delegation", False),
            output_format=agent_conf.get("output_format"),
            instructions=agent_conf.get("instructions"),
        )

    def _get_llm(self):
        llm_config = self.agents_config.get("default_llm", {}) or {}

        # Get API key from env or config
        env_api_key = os.getenv("GEMINI_API_KEY")
        final_api_key = env_api_key

        logger.info(f"🔑 Env API Key: {'SET' if env_api_key else 'MISSING'}")
        logger.info(f"🔑 Final API Key: {'SET' if final_api_key else 'MISSING'}")

        model = (
            llm_config.get("model")
            or os.getenv("LLM_MODEL")
            or "gemini/gemini-2.5-flash"
        )

        if "/" not in model and model.startswith("gemini"):
            model = f"gemini/{model}"

        if not final_api_key:
            logger.warning("❌ GEMINI_API_KEY not found!")
        
        logger.info(f"🔑 Using API Key: {final_api_key[:10]}..." if final_api_key else "❌ MISSING")
        logger.info(f"🤖 Using Model: {model}")

        return LLM(
            model=model,
            api_key=final_api_key,   # ✅ USE final_api_key
        )

    @task
    def script_generation_task(self) -> Task:
        task_conf = self.tasks_config.get("script_generation_task", {})
        logger.info(f"📝 Creating script_generation_task with JSON inspection requirement")
        return Task(
            description=task_conf.get("description", "Generate a draft script from Excel files using JSON inspection."),
            expected_output=task_conf.get("expected_output", "A draft Python script."),
            agent=self.script_generator(),
            execution_timeout=900,
        )

    @task
    def validation_task(self) -> Task:
        task_conf = self.tasks_config.get("validation_task", {})
        logger.info(f"📝 Creating validation_task with JSON-aware validation")
        return Task(
            description=task_conf.get("description", "Validate the generated script for accuracy against JSON inspection data."),
            expected_output=task_conf.get("expected_output", "A validated final Python script."),
            agent=self.validator(),
            output_file="final_script.py",
            execution_timeout=900,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the CsvOrganiser crew"""
        return Crew(
            agents=getattr(self, "agents", []),
            tasks=getattr(self, "tasks", []),
            process=Process.sequential,
            verbose=True,
            max_rounds=1,
        )