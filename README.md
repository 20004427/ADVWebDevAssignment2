To run the app:

It "should" work by simply cd'ing to the root.
Then running:       docker-compose build
followed by:        docker-compose up

Then going into docker desktop,
going into images,
clicking on the 'in use' symbol next to the image 'assignment2_app',
click on assignment2 (not the dropdown),
hover over 'flask-app' and click 'open in browser'.

NOTE: you must run the app via the docker-compose otherwise it will not work.
This is due to docker-compose overriding the ports in the dockerfile. Whilst, using docker run,
the ports specified in the dockerfile will be used.

As to how to specify the port when using docker-compose up, i'm not sure.
I cannot use the command in the deployment guild as it won't work for a docker-compose.
