from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from itinerary_dev_crew.tools.serper_tool import CustomSerperDevTool
from itinerary_dev_crew.tools.youtube_tool import YoutubeVideoSearchTool
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

load_dotenv()

# from crewai_tools import SerperDevTool

@CrewBase
class ItineraryDevCrewCrew():
	"""ItineraryDevCrew crew"""
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@agent
	def research_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['research_agent'],
			tools=[CustomSerperDevTool(), YoutubeVideoSearchTool()],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0.1)
		)

	@agent
	def itinerary_developer(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_developer'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0)
		)

	@agent
	def itinerary_geographical_expert(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_geographical_expert'],
			tools=[CustomSerperDevTool()],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0.05)
		)

	@agent
	def link_adding_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['link_adding_agent'],
			tools=[CustomSerperDevTool()],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0.05)
		)

	@agent
	def itinerary_translator_and_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['itinerary_translator_and_writer'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0.15)
		)

	@agent
	def message_reviser(self) -> Agent:
		return Agent(
			config=self.agents_config['message_reviser'],
			verbose=True,
			allow_delegation=False,
			llm=ChatOpenAI(model='gpt-4o', temperature=0)
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
			agent=self.research_agent()
		)

	@task
	def itinerary_task(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_task'],
			agent=self.itinerary_developer()
		)

	@task
	def itinerary_geo_organization(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_geo_organization'],
			agent=self.itinerary_geographical_expert()
		)

	@task
	def link_adding_task(self) -> Task:
		return Task(
			config=self.tasks_config['link_adding_task'],
			agent=self.link_adding_agent()
		)

	@task
	def itinerary_translation_and_writing(self) -> Task:
		return Task(
			config=self.tasks_config['itinerary_translation_and_writing'],
			agent=self.itinerary_translator_and_writer()
		)

	@task
	def outbound_message_revise(self) -> Task:
		return Task(
			config=self.tasks_config['outbound_message_revise'],
			agent=self.message_reviser()
		)

	@crew
	def crew(self) -> Crew:
		return Crew(
			agents=self.agents,  # Automatically created by the @agent decorator
			tasks=self.tasks,  # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=2,
			memory=False
		)
