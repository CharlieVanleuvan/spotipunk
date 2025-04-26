# spotipunk
This is a data pipeline that extracts songs from the reddit forum r/poppunkers and then sends those song titles to Spotify to build a playlist.
This project aims to showcase how GCP Cloud functions can be used and orchestrated to extract song titles from Reddit's API and then send those titles to Spotify's API to curate and maintain a playlist. 
## Design and Framework - GCP
On GCP, a python script will need to be deployed and scheduled to retrieve the latest songs mentioned in the popular subreddit. There are a few services available to handle that:
- Cloud Functions with Cloud Scheduler
    - **Cloud Functions:** This is a serverless execution environment for code. Deploy your script as a function without needing to manage underlying infrastructure. It scales automatically. Simple deployment, Auto-scaling, pay-for-what-you-use
    - **Cloud Scheduler:** This is a cron job that allows scheduling and can trigger cloud functions.
- Cloud Run with Cloud Scheduler
    - **Cloud Run:** This is a fully managed compute platform for deploying containerized applications. Allows for longer execution times and more control over the environment since it is deployed within a Docker container.
    - **Cloud Scheduler:** Same as above, but would send an HTTP request to Cloud Run service endpoint for the specific deployment
- Compute Engine with Cloud Scheduler
    - **Compute Engine:** This allows for creation and management of VMs to execute code which gives full control over environment creation and resources. Requires more management overhead and cost.
    - **Cloud Scheduler:** Same as above, but isn't necessary, since on the VM you can set it up to be active at certain times and execute a cron job that you set up on the VM.

Based on the above details, this pipeline will aim to be built with Cloud Functions and Cloud Scheduler, unless more management or execution time is necessary.
