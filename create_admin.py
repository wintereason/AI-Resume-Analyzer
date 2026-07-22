from auth import create_user


def main():
    try:
        user_id = create_user(
            full_name="HR Recruiter",
            username="recruiter",
            password="recruiter123",
            role="Recruiter",
        )

        print(f"Recruiter account created successfully. " f"User ID: {user_id}")

    except ValueError as error:
        print(f"Account not created: {error}")

    except Exception as error:
        print(f"Database error: {error}")


if __name__ == "__main__":
    main()
