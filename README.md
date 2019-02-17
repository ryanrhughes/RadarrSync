# RadarrSync 
RadarrSync Syncs two Radarr servers through web API. This is a modified version designed to be run in a docker container. This version supports only two servers.

## How to Run
https://cloud.docker.com/repository/docker/dmanius/radarrsync-docker

You need to pass in the following environment variables:
- RADARR_URL -> The endpoint of your radarr server
- RADARR_KEY -> The API key for your radarr server
- RADARR4K_URL -> The endpoint of your radarr server you want to sync to
- RADARR4K_KEY -> The API key for this server
- PROFILE_ID -> The profile number you want the video to transcode to

## Notes
 * Ensure that the root path is the same on both servers. ie /movie
