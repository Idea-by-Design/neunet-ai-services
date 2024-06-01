def upsert_resume(container, resume_data):
    try:
        container.upsert_item(resume_data)
        print("Data upserted successfully!")
    except Exception as e:
        print(f"An error occurred: {e}")
