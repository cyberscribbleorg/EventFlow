# EventFlow
Empower Your Git Project with Data-Driven Insights

## Setup (WIP)
1. Install Docker and Docker Compose for your environment.
2. Copy `env.copy` to `.env` and adjust parameters if required.
3. Configure `injector/config.json` parameters for harvest.
4. Run `docker-compose build` to build the containers and `docker-compose up` to spin up all instances.
5. Everything should work fine.

## Importing a Template Dashboard
- Access your Superset web interface.
- Go to **Dashboard** → **Import**.
- Select a dashboard from the template directory.
- Click **Import**.
- Enter the database password set in the `.env` file.

### FAQ: Database Connection Error After Importing a Dashboard
- Your `.env` configuration might be different from the default one (we export dashboards for default settings).
- Go to **Settings** → **Database Connections**.
- Select **mydatabase** connection and click **Edit** under actions.
- Reflect your specific database connection settings and test the connection.
- Everything should work fine.
