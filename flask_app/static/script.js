let isRunning = false
let currentStream = null
let videoEl = null
let currentAudio = null

window.onload = function(){
    fetch("/languages") // just receiving data
    .then(function(response){
        return response.json()
    })
    .then(function(data){
        // key - name, value - code
        for (let name in data){
            let code = data[name]
            if (code != "en") {
                let option = document.createElement("option")
                //'value''textContent' - displayed on webpage' are properties, cant be renamed
                option.value = code
                option.textContent = name
                document.getElementById("language").appendChild(option)
            }
        }
    })
    
    fetch("/reset")
}

document.getElementById("camera-button").addEventListener("change", function(){
    document.getElementById("file-input").style.display = "none" //hide file selector 
    document.getElementById("start").style.display = "block"
    document.getElementById("prompt").style.display = "none"
})

document.getElementById("video-button").addEventListener("change", function(){
    document.getElementById("file-input").style.display = "block" // show file selector
    document.getElementById("start").style.display = "none"
})

document.getElementById("video-file").addEventListener("change", function(){
    if (document.getElementById("video-file").files[0]){
        document.getElementById("start").style.display = "block"
    }
})

document.getElementById("start").addEventListener("click", function(){
    if (document.getElementById("video-button").checked) {
        if (document.getElementById("video-file").files[0] == undefined){
        // no file chosen after chosing a file previously - start button appears but should bot be functional
        document.getElementById("prompt").style.display = "block"
        document.getElementById("prompt").textContent = "Please select a video file"
        return
        }
    }
    document.getElementById("setup-screen").style.display = "none" //hidden
    document.getElementById("main-screen").style.display = "flex" //visible

    if (document.getElementById("camera-button").checked) {
        // the camera feed will open
        navigator.mediaDevices.getUserMedia({video: true}).then(function(stream){
            videoEl = document.getElementById("video-feed")
            videoEl.srcObject = stream
            currentStream = stream
            videoEl.addEventListener("loadeddata", function() {
                isRunning = true
                sendFrames(videoEl)
                },{once: true}) // wait 500ms for video to load
            })
        .catch(function(error){
            console.log("Camera error: ", error)
        })

    } else {
        // opens the video file
        document.getElementById("pause").style.display = "block"
        let file = document.getElementById("video-file").files[0]
        let url = URL.createObjectURL(file)
        videoEl = document.getElementById("video-feed")
        videoEl.src = url
        videoEl.addEventListener("loadeddata", function() {
            isRunning = true
            sendFrames(videoEl)
        })
        videoEl.addEventListener("ended", function(){
            isRunning = false
        })
    }
})

document.getElementById("language").addEventListener("change" , function(){
    fetch("/translate", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code : this.value})
    })
    .then(function(response){
        return response.json()
    })
    .then(function(data){
        document.getElementById("sentence").textContent = data // data is a normal json str
    })
})

document.getElementById("reset").addEventListener("click", function(){
    fetch("/reset")
    .then(function(){
        document.getElementById("confirmed-sign").textContent = ""
        document.getElementById("word-formed-so-far").textContent = ""
        document.getElementById("sentence").textContent = ""

        if (!currentStream){    //currentStrean = null is the video mode
            isRunning = false
            videoEl.pause()
            videoEl.currentTime = 0
            document.getElementById("pause").textContent = "resume"
            document.getElementById("prompt2").style.display = "block"
            document.getElementById("prompt2").textContent = "Click Resume to Start video"
        }       
    })
})

document.getElementById("end").addEventListener("click", function(){
    isRunning = false
    if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop())
    }
    if (videoEl){
        videoEl.pause()
        videoEl.src = ""
    }
    fetch("/reset")
    document.getElementById("main-screen").style.display = "none" //hidden
    document.getElementById("goodbye-screen").style.display = "flex" //visible

})

document.getElementById("speak").addEventListener("click", function(){
    fetch("/speak", {
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({code : document.getElementById("language").value})
    })
    .then(function(response){
        if (response.ok){
            return response.blob()
        }
    })
    .then(function(blob){
        if (blob){
            if (currentAudio){
                currentAudio.pause()
            }
            let url = URL.createObjectURL(blob)
            let audio = new Audio(url)
            currentAudio = audio
            audio.play()
        }
    })
})

document.getElementById("pause").addEventListener("click", function(){
    if(isRunning){ //pause 
        isRunning = false
        videoEl.pause()
        document.getElementById("pause").textContent = "Resume"
    }else { // then resume
        document.getElementById("prompt2").style.display = "none"
        isRunning = true
        videoEl.play()
        sendFrames(videoEl)
        document.getElementById("pause").textContent = "Pause"
    }
})

function sendFrames(video){
    if (!isRunning){
        return }

    let canvas = document.getElementById("canvas")
    // draw frames on the canvas
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    if (video.videoWidth === 0 || video.videoHeight === 0) {
    setTimeout(function(){
        if (isRunning){
            sendFrames(video)}}, 500)
    return
    }
    canvas.getContext("2d").drawImage(video,0,0)
    let Imagedata = canvas.toDataURL("image/jpeg")

    fetch("/predict",{     // receiving and sending data
        method: "POST",
        headers: {"Content-Type":"application/json"},
        body: JSON.stringify({image : Imagedata , language : document.getElementById("language").value})
    })
    .then(function(response){
        return response.json()
    })
    .then(function(data){
        document.getElementById("confirmed-sign").textContent = data.sign
        document.getElementById("word-formed-so-far").textContent = data.word
        document.getElementById("sentence").textContent = data.sentence
        if (isRunning){
        sendFrames(video)}
    })
}
