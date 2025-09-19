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

    agents_config_path: str = os.path.join(os.path.dirname(__file__), "agents.yaml")
    tasks_config_path: str = os.path.join(os.path.dirname(__file__), "tasks.yaml")

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
        return Agent(
            role=agent_conf.get("role", "Data Analyst"),
            goal=agent_conf.get("goal", "Generate a script from Excel files."),
            backstory=agent_conf.get("backstory", "You turn structured data into scripts."),
            verbose=True,
            tools=[excel_data_inspector_tool],
            llm=self._get_llm(),
            max_iter=agent_conf.get("max_iter", 2),
            max_execution_time=600,
            allow_delegation=agent_conf.get("allow_delegation", False),
            output_format=agent_conf.get("output_format"),
            instructions=agent_conf.get("instructions"),
        )

    @agent
    def validator(self) -> Agent:
        agent_conf = self.agents_config.get("validator", {})
        return Agent(
            role=agent_conf.get("role", "Reviewer"),
            goal=agent_conf.get("goal", "Check the generated script for accuracy."),
            backstory=agent_conf.get("backstory", "You validate correctness of generated scripts."),
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

        model = (
            llm_config.get("model")
            or os.getenv("LLM_MODEL")
            or "gemini/gemini-2.5-flash"
        )

        if "/" not in model and model.startswith("gemini"):
            model = f"gemini/{model}"

        api_key = (
            llm_config.get("api_key")
            or os.getenv("GEMINI_API_KEY")
        )

        if not api_key:
            logger.warning("❌ GEMINI_API_KEY not found!")

        logger.info(f"Configured LLM: {model}, api_key_set={'yes' if api_key else 'no'}")

        return LLM(
            model=model,
            api_key=api_key,
        )

    @task
    def script_generation_task(self) -> Task:
        task_conf = self.tasks_config.get("script_generation_task", {})
        return Task(
            description=task_conf.get("description", "Generate a draft script from Excel files."),
            expected_output=task_conf.get("expected_output", "A draft Python script."),
            agent=self.script_generator(),
            execution_timeout=900,
        )

    @task
    def validation_task(self) -> Task:
        task_conf = self.tasks_config.get("validation_task", {})
        return Task(
            description=task_conf.get("description", "Validate the generated script for accuracy."),
            expected_output=task_conf.get("expected_output", "A validated final Python script."),
            agent=self.validator(),
            output_file="final_script.py",  # 🔥 Save as .py instead of .md
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
