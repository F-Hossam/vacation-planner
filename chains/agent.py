from datetime import date
from langchain_openai import ChatOpenAI
from langchain.output_parsers import ResponseSchema, StructuredOutputParser, OutputFixingParser
from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

load_dotenv()

class GenerateAIResponse:
    _llm: ChatOpenAI = ChatOpenAI(temperature=0.6, model="gpt-3.5-turbo-0125")
    city_of_residence: str
    destination: str
    budget: float
    num_days: int
    hobbies: list[str]
    departure_date: date

    def __init__(self, destination: str, departure_date: date, num_days: int, hobbies: list[str], budget: float, domicile: str):
        self.city_of_residence = domicile
        self.destination = destination
        self.budget = budget
        self.num_days = num_days
        self.hobbies = hobbies
        self.departure_date = departure_date

    async def _make_request_template(self):
        response_schemas = [
            ResponseSchema(name="destination", description="The name of the destination"),
            ResponseSchema(name="travel_dates", description="The start and end dates of the travel"),
            ResponseSchema(name="itinerary", description="A day-by-day detailed travel itinerary. For each day, include at least 4 activities with timing (morning, afternoon, evening), meals, and transportation details."),
            ResponseSchema(name="budget_breakdown", description="A comprehensive breakdown of estimated costs for different categories including accommodation, food, activities, and transportation. Provide estimated costs for each item."),
            ResponseSchema(name="total_cost", description="The estimated total cost of the trip"),
            ResponseSchema(name="cost_range", description="The interval of estimated total cost (minimum and maximum)")
        ]

        output_parser = StructuredOutputParser.from_response_schemas(response_schemas)
        fixing_parser = OutputFixingParser.from_llm(parser=output_parser, llm=ChatOpenAI())
        format_instructions = output_parser.get_format_instructions()

        system_template="""
            As a travel agent. I have few informations to work with:
            City of residence: {domicile}.
            Favorite destination: {destination}.        
            I want to travel for {num_days} days from {date}.          
            My hobbies: {hobbies}.          
            My budget: {budget} dollars.

            Write a plan for this trip. It should be clair and entertaining.It should consider all the informations above.
            {format_instructions}
            Using the above instructions, output the response you think of.
        """

        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template, partial_variables={"format_instructions": format_instructions})
        human_request= """
                Please provide a detailed travel itinerary for each day of the trip. For each day:
                1. Include at least 4 detailed lines of activities or places to visit.
                2. Specify timing for each activity (morning, afternoon, evening).
                3. Mention any meals or dining experiences.
                4. Include any transportation details between activities.

                After the itinerary, provide a comprehensive budget breakdown:
                1. List all expected expenses categorized (e.g., accommodation, food, activities, transportation).
                2. Give an estimated cost for each item.

                Finally, give the overall cost range for the entire trip, considering potential variations in expenses.

                Please ensure all information aligns with the traveler's preferences, budget, and trip duration as specified in the system message.
            """
        chat_prompt = ChatPromptTemplate.from_messages(
            [system_message_prompt, MessagesPlaceholder("human_msg")]
        )

        request = chat_prompt.invoke({ #replace each input variable with its value using dict
                                "domicile": self.city_of_residence,
                                "destination": self.destination,
                                "num_days": self.num_days,
                                "date": self.departure_date,
                                "hobbies": self.hobbies,
                                "budget": self.budget,
                                "human_msg": [HumanMessage(content=human_request)]
                                }).to_messages()

        return (request,output_parser,fixing_parser)

    async def generate_response(self):
        request,output_parser,fixing_parser = await self._make_request_template()
        result = self._llm.invoke(request) #use model to generate a response for this request 

        try:
            parsed_output = output_parser.parse(result.content)
        except:
            parsed_output = fixing_parser.parse(result.content)

        result = {str(key): str(value) for key, value in parsed_output.items()}
        return result
    
    async def generate_other_options(self, message: str):
        request,output_parser,fixing_parser = await self._make_request_template()
        options_request = HumanMessage(message)
        request.append(options_request)
        result = self._llm.invoke(request)

        try:
            parsed_output = output_parser.parse(result.content)
        except:
            parsed_output = fixing_parser.parse(result.content)
        
        result = {str(key): str(value) for key, value in parsed_output.items()}
        return result
    

