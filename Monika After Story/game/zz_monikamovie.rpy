label ch30_monikamovie:
    init python:
        gamedir = os.path.normpath(config.gamedir)

        ## CLASS DEFINITIONS ##
        #This class holds all the information relative to
        # Monika's dialogue and reactios of the film
        class AvaiableMovies:
            def __init__(self):
                self.listOfMovies = []
                self.checkMovies()

            def checkMovies(self):
                with open(os.path.join(gamedir, "movies-info.txt"),"r") as f: #duplicated code
                    lines = f.readlines()
                listOfStrings = [x.strip() for x in lines]

                #Now we parse the info
                for line in listOfStrings:
                    if "#" in line:
                        continue
                    partialSplittedSentence = line.split(" ", 1)
                    firstWord = ""
                    if len(partialSplittedSentence) >= 2:
                        firstWord = partialSplittedSentence[0]
                        data = partialSplittedSentence[1]
                    if "movie" in firstWord:
                        self.listOfMovies.append(data)
            
            def searchMovies(self, movieName):
                foundMovies = []
                for xName in self.listOfMovies:
                    if movieName.lower() in xName.lower():
                        foundMovies.append(xName)
                return foundMovies

        class ParsedMovie:
            def __init__(self, movieName):
                self.descriptionList = []
                self.reactionList = []
                self.closureList = []
                self.currentReactionIndex = 0 #So monika can react again if user goes backwards
                self.retrieveMovie(movieName)

            def reactionsAreFinished(self):
                return self.currentReactionIndex >= len(self.reactionList)

            def stringReactionToTuple(self, string):
                emotion = None
                when = ""
                what = ""
                listOfInfo = []
                if not string[0] == "[": #with emotion
                    listOfInfo = string.split(" ", 2)
                    emotion = listOfInfo [0]
                    when = listOfInfo [1]
                    what = listOfInfo [2]
                else:
                    listOfInfo = string.split(" ", 1)
                    when = listOfInfo [0]
                    what = listOfInfo [1]
                return emotion,when,what

            def formattedTimeToSeconds(self, string):
                string = string.replace('[','')
                string = string.replace(']','')
                infoList = string.split(":")
                hours = int(infoList[0])
                minutes = int(infoList[1])
                seconds = int(infoList[2])
                return 3600*hours + 60*minutes + seconds

            def obtainCurrentReactionTuple(self):
                string = self.reactionList[self.currentReactionIndex]
                emotion, when, what = self.stringReactionToTuple(string)
                return emotion,when,what

            def popReaction(self):
                emotion, when, what = self.obtainCurrentReactionTuple()
                self.currentReactionIndex += 1
                return emotion,when,what


            def canReact(self, time):
                if(self.reactionsAreFinished()):
                    return False
                emotion, when, what = self.obtainCurrentReactionTuple()

                expectedToReact = self.formattedTimeToSeconds(when)
                return time > expectedToReact


            def popDescription(self):
                string = self.descriptionList.pop(0)
                stringArray = string.split(" ", 1)
                emotion = stringArray[0]
                line = stringArray[1]

                return emotion, line

            def hasDescription(self):
                return len(self.descriptionList) > 0

            def popClosure(self):
                string = self.closureList.pop(0)
                stringArray = string.split(" ", 1)
                emotion = stringArray[0]
                line = stringArray[1]

                return emotion, line

            def hasClosure(self):
                return len(self.closureList) > 0

            def formatData(self, data):
                return data.replace('"','')

            def retrieveMovie(self, movieName):
                with open(os.path.join(gamedir, "movies-info.txt"),"r") as f:
                    lines = f.readlines()
                listOfStrings = [x.strip() for x in lines]

                #Now we parse the info
                filmFound = False
                for line in listOfStrings:
                    if "#" in line:
                        continue
                    partialSplittedSentence = line.split(" ", 1)
                    firstWord = ""
                    if len(partialSplittedSentence) >= 2:
                        firstWord = partialSplittedSentence[0]
                        data = partialSplittedSentence[1]
                        data = self.formatData(data)
                    if "movie" in firstWord:
                        filmFound = movieName == partialSplittedSentence[1]
                    if filmFound:
                        if "description" == firstWord:
                            self.descriptionList.append(data)
                        if "m" == firstWord:
                            self.reactionList.append(data)
                        if "closure" == firstWord:
                            self.closureList.append(data)

            def resynchronizeIndex(self, timer):
                self.currentReactionIndex = 0
                while((not (self.reactionsAreFinished())) and self.canReact(timer.seconds)):
                    self.currentReactionIndex += 1


        class MovieTimer:
            def __init__(self):
                self.seconds = 0
            def seconds(self):
                return self.seconds
            def addSeconds(self, secondsAdded):
                self.seconds += secondsAdded
            def formattedTime(self):
                secondsPool = self.seconds
                hours = int(secondsPool / 3600)
                secondsPool -= hours * 3600
                minutes = int(secondsPool / 60)
                secondsPool -= minutes * 60
                secs = secondsPool
                return hours, minutes, secs
            def setFormattedTime(self,hours,minutes,seconds):
                self.seconds = int(hours)*3600 + int(minutes)*60 + int(seconds)


        ## FUNCTION DEFINITIONS ##
        def iterate_timer(st, at, timer):
            #Time calculations
            deltaTime = st - globals()['lastCountdownTime']
            globals()['lastCountdownTime'] = st
            if watchingMovie:
                timer.addSeconds(deltaTime)

            #Render
            hours, minutes, secs = timer.formattedTime()
            d = Text("%02d:%02d:%02d" % (hours, minutes, secs))
            return d, 0.1
        def fastforward(timer,secondsAdded):
            timer.addSeconds(secondsAdded)

        def updateEmotionMonika(emotion):
            if emotion is not None:
                monika_reaction = "monika %s" % (emotion)
                renpy.show(monika_reaction)


        ## VARIABLES USED IN THIS MODULE ##
        watchingMovie = False
        lastCountdownTime = 0 #Used as global variable, use with caution
        firstComment = False
        timer = MovieTimer()




    $ listMovies = AvaiableMovies()

    m 1b "You want to see a movie?"
    label choose_movie:
        menu:
            "Can you tell me the name?"
            "Yes":
                python:
                    player_dialogue = renpy.input('What is it? ',default='',pixel_width=720,length=50)
                    allFilms = listMovies.searchMovies(player_dialogue)
                    foundAnyFilm = len(allFilms) > 0
                if foundAnyFilm:
                    while(len(allFilms)>0):
                        $ renpy.say(eval("m"), "I've found a film named %s" % (allFilms[0]) )
                        menu:
                            "You want to see this one?"
                            "Yes":
                                m 1a "Nice! I wanted to see this one with you"
                                $ movieInformation = ParsedMovie(allFilms[0])
                                jump foundMovie
                            "No":
                                $ allFilms.pop(0)
                                m 1a "Let me search again"
                    m 1l "I can't finde more movies with that name"
                else:
                    m 1l "I didn't find any movie with that name"
                m "Maybe we should try with another one"
                jump choose_movie

            "Which films can you see?":
                m 1a "Let me see..."
                python:
                    LENGTH_RESTRICTION = 70
                    movieBuffer = ""
                    while(len(listMovies.listOfMovies) > 0):
                        movieBuffer += listMovies.listOfMovies.pop(0)
                        if len(movieBuffer) > LENGTH_RESTRICTION:
                            renpy.say(eval("m"), movieBuffer + "...")
                            movieBuffer = ""
                        else:
                            movieBuffer += ", "
                    if len(movieBuffer) > 0:
                        reemplacementBuffer = movieBuffer.rsplit(",",1)
                        movieBuffer = reemplacementBuffer[0] + "..."
                        renpy.say(eval("m"), movieBuffer)
                m 1a "And that's all of them"
                $ listMovies = AvaiableMovies()
                jump choose_movie





            "Nevermind":
                m 1a "Allright! maybe later"
                jump returnToLoop







    label foundMovie:
        $ MovieOverlayShowButtons()
        image countdown = DynamicDisplayable(iterate_timer, timer)
        show countdown at topleft
        #Starts description Block
        python:
            while(movieInformation.hasDescription()):
                emotion, what =  movieInformation.popDescription()
                updateEmotionMonika(emotion)
                renpy.say(eval("m"), what)
        m 1b "Lets synchronize the start of the film"
        m 1k "Get ready to start the film, I will do the countdown"

        menu:
            "Ready?"
            "Yes":
                label movie_resume:
                    $ allow_dialogue = False
                    m 1a "Three...{w=1}{nw}" 
                    m  "Two...{w=1}{nw}"
                    m  "One...{w=1}{nw}"
                    #Movie loop
                    $ watchingMovie = True
                    label movie_loop:
                        pause 1.0
                        python:
                            if movieInformation.canReact(timer.seconds):
                                emotion, when, what = movieInformation.popReaction()
                                updateEmotionMonika(emotion)
                                
                                if not (what == "" or what is None):
                                    what += "{w=10}{nw}"
                                    renpy.say(eval("m"), what)

                        if movieInformation.reactionsAreFinished():
                            jump closure

                        jump movie_loop

            "No":
                m 1b "Alright! I will just wait for you honey~"

        label closure:
            #Starts closure Block
            python:
                while(movieInformation.hasClosure()):
                    emotion, what =  movieInformation.popClosure()
                    updateEmotionMonika(emotion)
                    renpy.say(eval("m"), what)



    label returnToLoop:
        $ allow_dialogue = True
        $ watchingMovie = False
        $ timer.seconds = 0
        $ MovieOverlayHideButtons()
        show monika 1a
        hide countdown
        jump ch30_loop

    label pauseFilm:
        $ watchingMovie = False
        m 1b "Just stopped the movie"
        menu:
            "Do you wish to continue?"
            "Yes":
                jump movie_resume
            "No":
                m 1a "It's ok"
                jump returnToLoop

    label setTime:
        $ watchingMovie = False
        m 1b "You want to synchronize the time?"
        label repeatTime:
            m 1b "Tell me the time with format HH:MM:SS"
            python: 
                player_dialogue = renpy.input('What time should I set my movie? ',default='',pixel_width=720,length=50)
                splittedTime = player_dialogue.split(":",2)
                bad_format = len(splittedTime) != 3
                if not bad_format:
                    hours = splittedTime[0]
                    minutes = splittedTime[1]
                    seconds = splittedTime[2]
                    bad_format = not (hours.isdigit() and minutes.isdigit() and seconds.isdigit())
                    if not bad_format:
                        bad_format = int(minutes) >= 60 or int(seconds) >= 60
            if bad_format:
                m 1f "I can't understand it"
                m 1e "For example, for just 10 minutes and 23 seconds would be like:"
                m 1e "00:10:23"
                jump repeatTime
            else:
                $ timer.setFormattedTime(splittedTime[0],splittedTime[1],splittedTime[2])
                $ movieInformation.resynchronizeIndex(timer)
        m 1a "Done! Let's keep watching it"
        jump movie_resume





