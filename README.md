The purpose of this project is to build an automated web scraper for a Finnish real-estate website to scrape data of houses being sold and rented.

Scraper is built using Selenium and the data will be uploaded automatically to an Azure Blob Storage. 

The project is not completed, but the key aspects have been implemented:
- The scraper can ingest multiple different queries to target the scraping for specific subset of houses.
- The scraper has been running automatically for the last 2 months without any issues despite inadequate exception and error handling. 
- The scraped data is being uploaded to Azure Blob Storage account for further analysis.

Next steps:
- Start processing the downloaded data for analysis purposes.
- Visualize the data (average price, average sale time, etc.) on a map.
