from services.github_analysis.analyze_github import analyze_github_profile

def main():
    # Provide the GitHub identifier (username or URL) and candidate email for testing
    github_identifier = "HemantSingh11"
    candidate_email = "iamhks14@gmail.com"

    # Perform the analysis
    analysis_data = analyze_github_profile(github_identifier, candidate_email)

    # Print the analysis result
    print("Analysis Result:")
    print(analysis_data)

if __name__ == "__main__":
    main()
