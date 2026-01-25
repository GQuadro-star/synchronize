

window.onload = function ()
{
    let btn = document.querySelectorAll('#add_comment');
    let uls = document.querySelectorAll('#ul');
    for(let i = 0; i< uls.length; ++i)
    {
    let ti = document.getElementById("textInput")
    ti.id=i+"ti"
    console.log(ti.id)
    }
    for(let i = 0; i< btn.length; ++i)
    {
    btn[i].setAttribute('onclick', 'a('+i+')')
    console.log(i)
    uls[i].id=i+"ul"
    console.log(uls[i].id)
    loadComments(i)
    }
}






function a(button_number)
{
    console.log(button_number)
    let textInput = document.getElementById(button_number+"ti")
    let commentText = textInput.value
console.log("l="+commentText)
    if (commentText != '')
    {
console.log("a")
        let request = new XMLHttpRequest()
        let csrfToken = Cookies.get("csrftoken")
console.log("a")
        request.open(method="POST", url="/add_comment/", async=true)
        console.log("a")
        request.setRequestHeader("X-CSRFToken",csrfToken);
        console.log("b")
        request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
        console.log("c")
        request.onload = function()
        {
            console.log("d")
            let responseJSON = JSON.parse(request.response)
            console.log(responseJSON.status)
            loadComments(button_number)
        };
        let photo = button_number+1;
                console.log("comment="+JSON.stringify(comment=[commentText,photo]));
        request.send();
        }
    else {

        console.log("Введите данные в форму!")
    }


}
function loadComments(button_number)
{
    let request = new XMLHttpRequest()
    request.open(method="GET", url="/get_comments_data/", async=true)
    request.onload = function()
    {

        let responseJSON = JSON.parse(request.response)
        console.log(responseJSON)
        console.log("#"+button_number+"ul")
        console.log("5.JPEG".replace('.JPEG',""))
        let ConnentsList = document.getElementById(button_number+"ul")
        ConnentsList.innerHTML = ''
console.log("5.JPEG".replace('.JPEG',""))
let a = []
        for (let index = 0; index < responseJSON.data.length; ++index)
        {
            console.log("61.JPEG".replace('.JPEG',""))
            if(responseJSON.data[index].photo_id == button_number+1)
            {
                console.log("71")
                a.push(responseJSON.data[index].text);
            }
        }
        for (let index = 0; index < a.length; ++index)
        {
                console.log("7.JPEG".replace('.JPEG',""))
                ConnentsList.innerHTML += "<li class='list-group-item'>" + a[index] + "</li>"
                console.log("коментарий отправлен")
        }
    }
    request.send()
}