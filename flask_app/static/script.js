window.onload = function(){
    fetch("/languages")
    .then(function(resonse){
        return resonse.json()
    })
    .then(function(data){
        // key - name, value - code
        for (let name in data){
            let code = data[name]
            let option = document.createElement("option")
            //'value''textContent - displaed on webpage' are porperties, cant be renamed
            option.value = code
            option.textContent = name
            document.getElementById("language").appendChild(option)
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
            document.getElementById("video-feed").srcObject = stream
        })
        .catch(function(error){
            console.log("Camera error: ", error)
        })

    } else {
        // opens the video file
        let file = document.getElementById("video-file").files[0]
        let url = URL.createObjectURL(file)
        document.getElementById("video-feed").src = url
        // note: can be written in one line, but this is much cleaner to read

    }
})
