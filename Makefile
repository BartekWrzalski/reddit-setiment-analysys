env:
	@echo "CLIENT_ID=your_client_id" > .env
	@echo "CLIENT_SECRET=your_client_secret" >> .env
	@echo "USERNAME=your_reddit_username" >> .env
	@echo "PASSWORD=your_reddit_password" >> .env
	@echo "USER_AGENT=your_user_agent" >> .env
	@echo ".env file created. Please update it with your credentials."

install:
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt

run:
	streamlit run app.py --server.port 5000