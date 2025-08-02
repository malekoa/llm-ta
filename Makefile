# Variables
STREAMLIT_CMD=.venv/bin/streamlit run dashboard/app.py --server.address 0.0.0.0 --server.port 8501
FLASK_CMD=.venv/bin/python feedback/feedback_server.py
STREAMLIT_LOG=streamlit.log
FLASK_LOG=feedback.log
STREAMLIT_PID=streamlit.pid
FLASK_PID=flask.pid

.PHONY: start stop status restart logs setup

start:
	@echo "Starting Streamlit dashboard..."
	@if [ -f $(STREAMLIT_PID) ]; then \
		if kill -0 `cat $(STREAMLIT_PID)` 2>/dev/null; then \
			echo "Streamlit already running (PID `cat $(STREAMLIT_PID)`), skipping..."; \
		else \
			echo "Stale Streamlit PID file found, removing..."; \
			rm -f $(STREAMLIT_PID); \
			nohup $(STREAMLIT_CMD) > $(STREAMLIT_LOG) 2>&1 & echo $$! > $(STREAMLIT_PID); \
			echo "Streamlit restarted (PID `cat $(STREAMLIT_PID)`)."; \
		fi \
	else \
		nohup $(STREAMLIT_CMD) > $(STREAMLIT_LOG) 2>&1 & echo $$! > $(STREAMLIT_PID); \
		echo "Streamlit started (PID `cat $(STREAMLIT_PID)`)."; \
	fi
	@sleep 2
	@echo "Starting Feedback Flask server..."
	@if [ -f $(FLASK_PID) ]; then \
		if kill -0 `cat $(FLASK_PID)` 2>/dev/null; then \
			echo "Flask server already running (PID `cat $(FLASK_PID)`), skipping..."; \
		else \
			echo "Stale Flask PID file found, removing..."; \
			rm -f $(FLASK_PID); \
			nohup $(FLASK_CMD) > $(FLASK_LOG) 2>&1 & echo $$! > $(FLASK_PID); \
			echo "Flask restarted (PID `cat $(FLASK_PID)`)."; \
		fi \
	else \
		nohup $(FLASK_CMD) > $(FLASK_LOG) 2>&1 & echo $$! > $(FLASK_PID); \
		echo "Flask started (PID `cat $(FLASK_PID)`)."; \
	fi
	@echo "Both apps checked (logs: $(STREAMLIT_LOG), $(FLASK_LOG))."

stop:
	@echo "Stopping Streamlit dashboard..."
	@if [ -f $(STREAMLIT_PID) ]; then \
		if kill -0 `cat $(STREAMLIT_PID)` 2>/dev/null; then \
			kill -TERM `cat $(STREAMLIT_PID)` && echo "Streamlit stopped."; \
		else \
			echo "Streamlit process not running, cleaning stale PID file."; \
		fi; \
		rm -f $(STREAMLIT_PID); \
	else \
		echo "No Streamlit PID file, skipping."; \
	fi
	@echo "Stopping Feedback Flask server..."
	@if [ -f $(FLASK_PID) ]; then \
		if kill -0 `cat $(FLASK_PID)` 2>/dev/null; then \
			kill -TERM `cat $(FLASK_PID)` && echo "Flask stopped."; \
		else \
			echo "Flask process not running, cleaning stale PID file."; \
		fi; \
		rm -f $(FLASK_PID); \
	else \
		echo "No Flask PID file, skipping."; \
	fi
	@echo "All apps stopped."

status:
	@echo "Checking processes..."
	@if [ -f $(STREAMLIT_PID) ]; then \
		if kill -0 `cat $(STREAMLIT_PID)` 2>/dev/null; then \
			ps -p `cat $(STREAMLIT_PID)` -o pid=,cmd=; \
		else \
			echo "Streamlit PID file exists but process is not running (stale)."; \
		fi; \
	else \
		echo "Streamlit not running"; \
	fi
	@if [ -f $(FLASK_PID) ]; then \
		if kill -0 `cat $(FLASK_PID)` 2>/dev/null; then \
			ps -p `cat $(FLASK_PID)` -o pid=,cmd=; \
		else \
			echo "Flask PID file exists but process is not running (stale)."; \
		fi; \
	else \
		echo "Flask not running"; \
	fi

restart: stop start

logs:
	@echo "Tailing logs (Ctrl+C to exit)..."
	@tail -n 30 -f $(STREAMLIT_LOG) $(FLASK_LOG)

setup:
	@echo "Running setup script..."
	@bash setup.sh