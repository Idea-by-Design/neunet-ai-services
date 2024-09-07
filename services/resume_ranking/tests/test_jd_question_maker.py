import os
from ..jd_question_maker import generate_questionnaire, save_questionnaire

def main():
    # Mock API Key (Replace this with a real API key or retrieve it from environment variables)
    api_key = os.getenv("OPENAI_API_KEY")

    # Sample Job Description
    job_description = """
    Machine Learning Scientist
    
    About the job
    Machine Learning Scientist, Machine Learning (Active Learning & Bayesian Optimization)

    Onsite in Cambridge, Massachusetts, USA

    We are seeking a talented (Senior) Machine Learning Scientist with expertise in Active Learning and Bayesian Optimization, to join our innovative team in Cambridge, Massachusetts.

    Key Responsibilities:

    Design, build, and scale supervised ML models for Active Learning and Bayesian optimization in materials synthesis and performance.
    Implement best practices and innovate methods for uncertainty quantification.
    Integrate datasets of multiple fidelities and sources for data-driven materials discovery.
    Collaborate with the computational team to identify materials design pathways and their synthesis.
    Work with infrastructure and automation teams for real-time data and prediction transfers.
    Drive material discovery and development with the experimental team, building domain-specific acquisition functions.
    Stay updated on ML research through literature reviews, conferences, and networking.
    Report findings to stakeholders and leadership through written reports and presentations.

    Qualifications:

    Experience with uncertainty quantification, active learning, and Bayesian optimization.
    Skilled in implementing, evaluating, and tuning supervised models in a Bayesian optimization context.
    Proficiency in ML frameworks (PyTorch/TensorFlow/Jax) and the Python data science ecosystem (Numpy, SciPy, Pandas, etc.).
    Experience with cloud computing services for training and evaluating models.
    PhD in Computer Science, Applied Mathematics, or a related field with a focus on ML.
    Independent thinker with strong attention to detail.
    Demonstrated industry experience or notable academic achievement.
    Excellent communication and presentation skills.
    Enthusiastic about working in a fast-paced, entrepreneurial, and technical setting.

    Preferred Qualifications:

    Experience using AWS services.
    Experience with integrating machine learning in experimental workflows.
    """

    # Output folder and filename
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Get the current script directory
    output_folder = os.path.join(current_dir, "job_questionnaire_results")  # Ensure 'output' folder is created in the current script's directory
    output_filename = "job_questionnaire.txt"  

    # Generate questionnaire using the job description
    print("Generating questionnaire...")
    questionnaire = generate_questionnaire(job_description)

    # Save the questionnaire to a JSON file
    print("Saving questionnaire to JSON...")
    output_path = save_questionnaire(questionnaire, output_folder, output_filename)

    # Confirm completion
    print(f"Questionnaire saved at: {output_path}")

if __name__ == '__main__':
    main()
    # way to run: python -m services.resume_ranking.tests.test_jd_question_maker 
