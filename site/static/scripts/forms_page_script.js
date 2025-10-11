function setOneForm()
{
    let divCards = document.querySelectorAll(".cards-col")
    for (let index = 0; index < divCards.length; ++index)
    {
        if (divCards[index].classList.contains("col-6"))
        {
            divCards[index].classList.remove("col-6")
        }
        if (divCards[index].classList.contains("col-4"))
        {
            divCards[index].classList.remove("col-4")
        }
        divCards[index].classList.add("col-12")
    }
}
function setTwoForms()
{
    let divCards = document.querySelectorAll(".cards-col")
    for (let index = 0; index < divCards.length; ++index)
    {
        if (divCards[index].classList.contains("col-12"))
        {
            divCards[index].classList.remove("col-12")
        }
        if (divCards[index].classList.contains("col-4"))
        {
            divCards[index].classList.remove("col-4")
        }
        divCards[index].classList.add("col-6")
    }
}
function setThreeForms()
{
    let divCards = document.querySelectorAll(".cards-col")
    for (let index = 0; index < divCards.length; ++index)
    {

        if (divCards[index].classList.contains("col-12"))
        {
            divCards[index].classList.remove("col-12")
        }
        if (divCards[index].classList.contains("col-6")) {
            divCards[index].classList.remove("col-6")
        }
        divCards[index].classList.add("col-4")
    }
}