import os
import json
from dotenv import load_dotenv
from ..agent_call import initiate_chat
# Load environment variables
load_dotenv()

# Ensure you have set the OPENAI_API_KEY in your .env file
if "OPENAI_API_KEY" not in os.environ:
    raise EnvironmentError("Please set the OPENAI_API_KEY environment variable in your .env file")

# Mock data
mock_resume_1 = """
    # John Doe
    123 Tech Street, Cambridge, MA 02139 | john.doe@email.com | (555) 123-4567

    ## Summary
    Experienced Machine Learning Scientist with a strong background in Active Learning and Bayesian Optimization. PhD in Computer Science with a focus on machine learning. Skilled in implementing and scaling supervised ML models for materials discovery and optimization.

    ## Education
    **PhD in Computer Science, Machine Learning Focus**
    Massachusetts Institute of Technology, Cambridge, MA
    2015 - 2020

    **MS in Applied Mathematics**
    Stanford University, Stanford, CA
    2013 - 2015

    **BS in Computer Science**
    University of California, Berkeley, CA
    2009 - 2013

    ## Professional Experience
    **Senior Machine Learning Scientist**
    TechInnovate AI, Cambridge, MA
    2020 - Present

    - Designed and implemented active learning algorithms for materials synthesis optimization, resulting in a 30% reduction in experimental iterations.
    - Developed Bayesian optimization techniques for multi-fidelity data integration, improving prediction accuracy by 25%.
    - Collaborated with computational and experimental teams to drive materials discovery, resulting in 3 patent applications.
    - Implemented uncertainty quantification methods, enhancing model reliability and decision-making processes.
    - Led a team of 4 ML engineers in developing a cloud-based platform for real-time data processing and model predictions.

    **Machine Learning Research Intern**
    Google AI, Mountain View, CA
    Summer 2019

    - Contributed to the development of novel active learning strategies for large-scale image classification tasks.
    - Implemented and evaluated Bayesian neural network architectures for uncertainty estimation in computer vision applications.

    ## Skills
    - Programming: Python (NumPy, SciPy, Pandas, Scikit-learn), PyTorch, TensorFlow, JAX
    - Cloud Computing: AWS (EC2, S3, SageMaker)
    - Machine Learning: Active Learning, Bayesian Optimization, Uncertainty Quantification, Supervised Learning
    - Version Control: Git, GitHub
    - Data Visualization: Matplotlib, Seaborn, Plotly

    ## Publications
    1. Doe, J., et al. (2021). "Active Learning for Materials Discovery: A Bayesian Optimization Approach." Nature Materials.
    2. Doe, J., & Smith, A. (2020). "Uncertainty Quantification in Multi-Fidelity Material Property Prediction." Machine Learning for Materials Science.

    ## Awards
    - Best Paper Award, International Conference on Machine Learning (ICML), 2022
    - Outstanding Doctoral Thesis Award, MIT Computer Science Department, 2020

    ## Professional Memberships
    - Member, Association for Computing Machinery (ACM)
    - Member, Institute of Electrical and Electronics Engineers (IEEE)
"""

mock_resume_2= """
    # Jane Smith
    456 Web Avenue, Boston, MA 02108 | jane.smith@email.com | (555) 987-6543

    ## Summary
    Dedicated Front-End Engineer with 5 years of experience in creating responsive and user-friendly web applications. Proficient in modern JavaScript frameworks and passionate about delivering exceptional user experiences.

    ## Education
    **BS in Computer Science**
    Boston University, Boston, MA
    2014 - 2018

    ## Professional Experience
    **Senior Front-End Engineer**
    WebTech Solutions, Boston, MA
    2021 - Present

    - Lead the front-end development of a high-traffic e-commerce platform, improving load times by 40% through optimization techniques.
    - Implemented responsive designs using HTML5, CSS3, and JavaScript, ensuring cross-browser compatibility and mobile responsiveness.
    - Collaborated with UX designers to create intuitive user interfaces, increasing user engagement by 25%.
    - Mentored junior developers and conducted code reviews to maintain high code quality standards.

    **Front-End Developer**
    Digital Creations Inc., Cambridge, MA
    2018 - 2021

    - Developed and maintained multiple client websites using React.js and Vue.js frameworks.
    - Integrated RESTful APIs to create dynamic web applications with real-time data updates.
    - Implemented state management solutions using Redux and Vuex for complex application architectures.
    - Utilized Webpack and Babel for efficient code bundling and cross-browser compatibility.

    ## Skills
    - Programming: JavaScript (ES6+), HTML5, CSS3, TypeScript
    - Frameworks/Libraries: React.js, Vue.js, Angular
    - State Management: Redux, Vuex
    - CSS Preprocessors: Sass, Less
    - Version Control: Git, GitLab
    - Build Tools: Webpack, Babel, npm
    - Testing: Jest, Enzyme, Cypress
    - UI/UX: Responsive Design, Material-UI, Bootstrap
    - Performance Optimization: Lazy Loading, Code Splitting

    ## Projects
    **Personal Portfolio Website**
    - Designed and developed a responsive personal portfolio website using React.js and Gatsby.
    - Implemented a custom CSS grid system for layout flexibility and responsiveness.

    **Weather Dashboard Application**
    - Created a weather dashboard using Vue.js, integrating with a third-party weather API.
    - Implemented geolocation features and local storage for improved user experience.

    ## Certifications
    - AWS Certified Cloud Practitioner
    - Google Analytics Individual Qualification

    ## Professional Development
    - Regular attendee of local web development meetups and conferences
    - Contributed to open-source projects on GitHub

    ## Languages
    - English (Native)
    - Spanish (Conversational)
"""

mock_job_description = """
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

mock_candidate_email_1 = "john.doe@example.com"
mock_candidate_email_2 = "jane.smith@example.com"

# Function to load a file as a string
def load_file_content(file_path):
    with open(file_path, 'r') as file:
        return file.read()

def print_json_content():
    try:
        with open("ranking_data.json", "r") as file:
            data = json.load(file)
            print("Contents of ranking_data.json:")
            print(json.dumps(data, indent=2))
    except FileNotFoundError:
        print("ranking_data.json file not found.")
    except json.JSONDecodeError:
        print("Error decoding JSON from ranking_data.json.")
        
        
def test_resume_ranking():
    import os
    print("Current working directory:", os.getcwd())
    questionnaire_path = r"services\resume_ranking\tests\job_questionnaire_results\job_questionnaire.txt"
    questionnaire_content = load_file_content(questionnaire_path)
    print("Starting resume ranking test...")
    result = initiate_chat(mock_resume_1, mock_job_description, mock_candidate_email_1, questionnaire_content)
    print("Test completed. Check the ranking_data.json file for results.")
    print("\nPrinting contents of ranking_data.json:")
    print_json_content()
    return result

if __name__ == "__main__":
    test_resume_ranking()