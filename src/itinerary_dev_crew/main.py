# import sys
import argparse
from itinerary_dev_crew.crew import ItineraryDevCrewCrew
from dotenv import load_dotenv
import os

load_dotenv()
os.getenv('OPENAI_MODEL_NAME')
os.getenv('OPENAI_API_KEY')

def get_inputs_from_args(args):
    return {
        'names': args.names,
        'num_travelers': args.num_travelers,
        'origin': args.origin,
        'destination': args.destination,
        'hotel_name': args.hotel_name,
        'hotel_address': args.hotel_address,
        'flight_outward_arrival_time': args.flight_outward_arrival_time,
        'breakfast_included': args.breakfast_included,
        'flight_return_departure_time': args.flight_return_departure_time,
        'ages': args.ages,
        'start_date': args.start_date,
        'end_date': args.end_date,
        'flight_data': args.flight_data
    }

def run(args):
    inputs = get_inputs_from_args(args)
    ItineraryDevCrewCrew().crew().kickoff(inputs=inputs)

def train(args):
    inputs = get_inputs_from_args(args)
    try:
        ItineraryDevCrewCrew().crew().train(n_iterations=args.iterations, inputs=inputs)
    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def main():
    parser = argparse.ArgumentParser(description="Itinerary Development Crew Script")
    parser.add_argument('--names', required=True, help="Names of the travelers, separated by commas")
    parser.add_argument('--num_travelers', type=int, required=True, help="Number of travelers")
    parser.add_argument('--origin', required=True, help="Origin city")
    parser.add_argument('--destination', required=True, help="Destination city")
    parser.add_argument('--hotel_name', required=True, help="Name of the hotel")
    parser.add_argument('--hotel_address', required=True, help="Address of the hotel")
    parser.add_argument('--flight_outward_arrival_time', required=True, help="Outward flight arrival time")
    parser.add_argument('--breakfast_included', required=True, help="Is breakfast included?")
    parser.add_argument('--flight_return_departure_time', required=True, help="Return flight departure time")
    parser.add_argument('--ages', required=True, help="Ages of the travelers, separated by commas")
    parser.add_argument('--start_date', required=True, help="Start date of the trip")
    parser.add_argument('--end_date', required=True, help="End date of the trip")
    parser.add_argument('--flight_data', required=True, help="Flight details")
    parser.add_argument('--iterations', type=int, help="Number of iterations for training")

    args = parser.parse_args()

    if args.iterations:
        train(args)
    else:
        run(args)

if __name__ == "__main__":
    main()