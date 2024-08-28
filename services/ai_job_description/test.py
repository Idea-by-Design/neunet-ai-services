from generate_description import generate_description

# Sample input data for testing
test_data = {
    'job_id': '12345',
    'title': '',
    'company_name': '',
    'location': '',
    'type': '',
    'time_commitment': '',
    'description': '',
    'requirements': '',
    'benefits': 'Health insurance, 401(k)'
}

generated_description = generate_description(test_data)
print("Generated Job Description:\n")
print(generated_description)
