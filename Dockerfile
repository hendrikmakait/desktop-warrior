FROM node:alpine

# Create user 'hendrikmakait' with home directory
RUN adduser -D -h /Users/hendrikmakait hendrikmakait

# Create the filesystem structure
RUN mkdir -p /Users/hendrikmakait/Desktop
RUN mkdir -p /Users/hendrikmakait/Documents

# Create a messy desktop
WORKDIR /Users/hendrikmakait/Desktop

RUN touch "Screenshot 2025-10-01 at 08.30.00.png"
