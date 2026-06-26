window.onload = function(){
    fetch("/languages") // just receiving data
    .then(function(resonse){
        return resonse.json()
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
}

document.getElementById("camera-button").addEventListener("change", function(){
    document.getElementById("file-input").style.display = "none" //hide file selector 
    document.getElementById("start").style.display = "block"
})

document.getElementById("video-button").addEventListener("change", function(){
    document.getElementById("file-input").style.display = "block" // show file selector
})

document.getElementById("video-file").addEventListener("change", function(){
        document.getElementById("start").style.display = "block"
    })

document.getElementById("start").addEventListener("click", function(){
    document.getElementById("setup-screen").style.display = "none" //hidden
    document.getElementById("main-screen").style.display = "block" //visible

    if (document.getElementById("camera-button").checked) {
        // the camera feed will open
        navigator.mediaDevices.getUserMedia({video: true}).then(function(stream){
            let videoEl = document.getElementById("video-feed")
            videoEl.srcObject = stream
                videoEl.addEventListener("loadeddata", function() {
                sendFrames(videoEl)
                }) // wait 500ms for video to load
        })
        .catch(function(error){
            console.log("Camera error: ", error)
        })

    } else {
        // opens the video file
        let file = document.getElementById("video-file").files[0]
        let url = URL.createObjectURL(file)
        let videoEl = document.getElementById("video-feed")
            videoEl.src = url
            videoEl.addEventListener("loadeddata", function() {
                sendFrames(videoEl)
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

function sendFrames(video){
    let canvas = document.getElementById("canvas")
    // draw frames on the canvas
    canvas.width = video.videoWidth
    canvas.height = video.videoHeight
    if (video.videoWidth === 0 || video.videoHeight === 0) {
    setTimeout(function(){sendFrames(video)}, 500)
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
        sendFrames(video)
    })
}
