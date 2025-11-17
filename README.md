# LookUp

#### Video Demo:  [CS50 MY FINAL PROJECT - DEMO](https://www.youtube.com/watch?v=S-o-HmI6fNw)
#### Video Walkthrough: [CS50 MY FINAL PROJECT - WALKTHROUGH](https://www.youtube.com/watch?v=0Kxk0gI6H3I)

-------------------

#### Description
LookUp is a full-stack web application built as my CS50 final project. It's an organized information tool of technical reference material, in my case, more technical - it could be "LookUp - Plants" for example - solving the common problem of scattered notes and code snippets across different platforms. The application provides a clean, searchable interface for browsing cheat sheets and technical guides while featuring a dynamic admin dashboard for content management.

It's a Flask-based backend, a Python web framework chosen primarily for the simplicity and control that it provides. LookUp uses pure JavaScript, HTML, and CSS. This approach keeps the application lightweight and showcases what can be done with core web technologies.

The application follows the Model-View-Controller pattern: in the models folder, the data layer is implemented, where each file is assigned responsibility for specific database operations. Also, a custom decorator manages database connections automatically so the code accessing the data is clean and uniform in every operation. Routes act as traffic controllers that process a request and manage interaction between different models and templates.

Templates define the layout for all web pages. A base layout template typically defines common elements, such as navigation and footer. This ensures a consistent design throughout the site and makes updating global parts easier. The static assets are organized into separate CSS files for handling themes, layout, and components. JavaScript animates the interface, features such as search, theme switchers, and drag-and-drop content management.

The application is deployed on an Ubuntu server, using PM2 for process management and Nginx as a reverse proxy. This setup is reliable and offers 24/7 availability. Other utilities are image processing and file uploading, keeping the application lightweight and organized.

The goal with LookUp was a design that should be minimalistic, where the users can see useful notes and the admins can easily edit the site without having to edit code.

There are many extra features I could have implemented, and I’m sure there are bug fixes I haven’t noticed or were unable to fix. As much as I would have loved to continue improving the site, I think it's best I move onto a new project now! 

This is a summary of what was said in my walkthrough video.
