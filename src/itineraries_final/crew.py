from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai_tools import WebsiteSearchTool
from itineraries_final.tools.accuweather_tool import AccuWeatherTool
from itineraries_final.tools.viator_activity_tool import ViatorTopProductsTool
from itineraries_final.tools.distance_matrix_tool import LocationStatusDistanceTool
from itineraries_final.tools.perplexity_tool import RealTimeSearchTool
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic

@CrewBase
class ItinerariesFinal():
    """BusinessAutomationIntroduction crew"""

    @agent
    def research_agent(self) -> Agent:
        return Agent(
            config=self.agents_config['research_agent'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def itinerary_developer(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_developer'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def itinerary_translator_and_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['itinerary_translator_and_writer'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def PR_director(self) -> Agent:
        return Agent(
            config=self.agents_config['PR_director'],
            verbose=True,
            allow_delegation=False
        )

    @agent
    def Itinerary_Director(self) -> Agent:
        return Agent(
            config=self.agents_config['Itinerary_Director'],
            verbose=True,
            allow_delegation=False
        )

    @task
    def gather_viator_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['gather_viator_data_task'],
            tools=[ViatorTopProductsTool()],
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm=ChatOpenAI(model='o1-mini', temperature=0)
        )

    @task
    def fetch_weather_data_task(self) -> Task:
        return Task(
            config=self.tasks_config['fetch_weather_data_task'],
            tools=[AccuWeatherTool()],
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm=ChatOpenAI(model='gpt-4o-mini', temperature=0.05)
        )

    @task
    def web_search_additional_research_task(self) -> Task:
        return Task(
            config=self.tasks_config['web_search_additional_research_task'],
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm=ChatOpenAI(model='gpt-4o', temperature=0.1)
        )

    @task
    def date_specific_events_task(self) -> Task:
        return Task(
            config=self.tasks_config['date_specific_events_task'],
            tools=[RealTimeSearchTool()],
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm=ChatOpenAI(model = 'gpt-4o', temperature = 0.05)
        )

    @task
    def itinerary_task(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_task'],
            agent=self.itinerary_developer(),
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm = ChatOpenAI(model = 'o1-preview', temperature = 0.1)
        )

    @task
    def directions_task(self) -> Task:
        return Task(
            config=self.tasks_config['directions_task'],
            tools=[LocationStatusDistanceTool()],
            agent = self.research_agent(),
            verbose=True,
            allow_delegation=False,
            async_execution=False,
            llm=ChatOpenAI(model='gpt-4o', temperature=0.05)
        )

    @task
    def itinerary_translation_and_writing(self) -> Task:
        return Task(
            config=self.tasks_config['itinerary_translation_and_writing'],
            llm=ChatOpenAI(model = 'gpt-4o', temperature = 0)
        )

    @task
    def PR_adaptation(self) -> Task:
        return Task(
            config=self.tasks_config['PR_adaptation'],
            llm = ChatAnthropic(model = 'claude-3-5-sonnet-20241022',
                                temperature = 0)
        )

    @task
    def Itinerary_Curation(self) -> Task:
        return Task(
            config=self.tasks_config['Itinerary_Curation'],
            llm = ChatOpenAI(model = 'o1-preview')
        )

    @crew
    def crew(self) -> Crew:
        """Creates the BusinessAutomationIntroduction crew"""
        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory = False,
            cache = False
        )
