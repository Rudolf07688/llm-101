from crewai import Agent, Task, Crew

# Create a simple chat agent
chat_agent = Agent(
    role="Friendly Chat Assistant",
    goal="Provide helpful and friendly responses to user queries",
    backstory="You are a helpful assistant designed to chat with users and provide information on various topics.",
    verbose=True
)

# Define a task for the chat agent
chat_task = Task(
    description="Respond to the user's message in a helpful and friendly manner.",
    expected_output="A clear and concise response to the user's query.",
    agent=chat_agent
)

# Create a crew with just the chat agent
crew = Crew(
    agents=[chat_agent],
    tasks=[chat_task]
)

# Function to handle chat interaction
def chat_with_agent(user_input):
    result = crew.kickoff(inputs={"query": user_input})
    return result

# Simple chat loop
if __name__ == "__main__":
    print("Simple CrewAI Chat Agent (type 'exit' to quit)")
    print("----------------------------------------------")
    
    while True:
        user_message = input("You: ")
        if user_message.lower() == 'exit':
            print("Chat ended. Goodbye!")
            break
            
        response = chat_with_agent(user_message)
        print(f"Agent: {response}")
