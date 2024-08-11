def generate_description(data):
    # Use an AI model to generate the job description based on the input
    # Possibly load prompt template and fill it with data
    prompt = load_prompt()
    # Call to the AI model service, e.g., GPT, to generate a job description
    # This is a placeholder
    generated_description = call_ai_model(prompt)
    return generated_description

def load_prompt():
    with open('services/ai_job_description/prompts/generate_prompt.txt', 'r') as file:
        return file.read()

def call_ai_model(prompt):
    # Logic to call an AI model (e.g., OpenAI API or custom model)
    pass
