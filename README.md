\# 🌍 IoT Environmental Monitoring Dashboard



A cloud-integrated environmental monitoring system built using \*\*Python, Streamlit, and AWS\*\*. The project simulates IoT sensor readings, stores environmental data in the cloud, and visualizes measurements through an interactive web dashboard.



\## 📌 Project Overview



The IoT Environmental Monitoring Dashboard helps users monitor environmental conditions, analyze sensor trends, and identify potentially unsafe readings.



The system uses AWS services for automated data generation, cloud storage, and API-based data retrieval.



\## 🚀 Features



\- 📊 \*\*Overview:\*\* Environmental metrics and monitoring summary

\- 📈 \*\*Sensor Analytics:\*\* Interactive charts and sensor trends

\- 🚨 \*\*Environmental Alerts:\*\* Warning and critical threshold detection

\- ☁️ \*\*Cloud Status:\*\* AWS integration and connectivity information

\- 📋 \*\*Sensor History:\*\* Historical readings, date filtering, and CSV export

\- 🔄 \*\*Data Refresh:\*\* Manual refresh and automatic refresh options



\## 🛠️ Technologies Used



| Technology | Purpose |

|---|---|

| Python | Application development |

| Streamlit | Interactive web dashboard |

| Pandas | Data processing |

| Plotly | Data visualization |

| AWS Lambda | Serverless data processing |

| Amazon DynamoDB | NoSQL sensor data storage |

| Amazon API Gateway | REST-style HTTP API access |

| Amazon EventBridge Scheduler | Automated sensor data generation |

| GitHub | Source code management |



\## 🏗️ System Architecture



```text

IoT Sensor Simulator

&#x20;       |

&#x20;       v

Amazon EventBridge Scheduler

&#x20;       |

&#x20;       v

AWS Lambda (Data Writer)

&#x20;       |

&#x20;       v

Amazon DynamoDB

&#x20;       |

&#x20;       v

AWS Lambda (Data Reader)

&#x20;       |

&#x20;       v

Amazon API Gateway

&#x20;       |

&#x20;       v

Streamlit Dashboard

&#x20;       |

&#x20;       v

Charts | Alerts | Sensor History

```



\## 📊 Environmental Parameters



The system monitors:



\- Temperature (°C)

\- Humidity (%)

\- Air Quality (simulated index)

\- CO₂ Concentration (ppm)



The project uses simulated sensor measurements for demonstration and testing purposes.



\## ⚙️ Installation



Clone the repository:



```bash

git clone https://github.com/YOUR\_USERNAME/IoT-Environmental-Monitoring-Dashboard.git

cd IoT-Environmental-Monitoring-Dashboard

```



Install dependencies:



```bash

pip install -r requirements.txt

```



Run the dashboard:



```bash

python -m streamlit run dashboard.py

```



Open the local dashboard:



`http://localhost:8501`



\## ☁️ AWS Integration



The system uses Amazon EventBridge Scheduler to trigger a Lambda function that generates simulated environmental readings.



These readings are stored in Amazon DynamoDB.



A second Lambda function retrieves the stored data and makes it accessible through Amazon API Gateway.



The Streamlit dashboard uses the API to display environmental metrics and historical readings.



\*\*Note:\*\* AWS Academy lab resources are temporary. Live cloud functionality depends on the availability of the configured AWS environment.



\## 🚀 Deployment



The dashboard is intended for deployment using Streamlit Community Cloud.



\*\*Live Dashboard:\*\* Coming soon.



\## 🔮 Future Enhancements



\- Physical IoT sensor integration

\- Email or SMS alert notifications

\- Predictive environmental analytics

\- Multiple sensor and device support

\- Long-term cloud hosting



\## 📄 Project Type



Academic and portfolio project demonstrating IoT simulation, cloud computing, serverless architecture, API integration, and interactive data visualization.

