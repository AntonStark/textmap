"use strict";
console.debug('paragraphScroll.js loaded');


function isVisible(elem) {
    let coords = elem.getBoundingClientRect();
    let windowHeight = document.documentElement.clientHeight;

    // верхний край элемента виден?
    let topVisible = coords.top > 0 && coords.top < windowHeight;
    // нижний край элемента виден?
    let bottomVisible = coords.bottom < windowHeight && coords.bottom > 0;

    return topVisible || bottomVisible;
}

// may return null
function getTopVisiblePrecedingSibling(baseElement) {
    while (baseElement) {
        const previousElement = baseElement.previousElementSibling;
        if (isVisible(baseElement) && !isVisible(previousElement))
            break;
        baseElement = previousElement;
    }
    return baseElement;
}
function getTopVisibleFollowingSibling(baseElement) {
    while (baseElement) {
        if (isVisible(baseElement))
            break;
        baseElement = baseElement.nextElementSibling;
    }
    return baseElement;
}

let previousPageYOffset = 0;
let mostTopParagraph;
// Обработчик скрола следит за актуальностью глобальной ссылки на верхний хотя бы частично видимый абзац
let scrollHandler = function () {
    let scrollForward = pageYOffset > previousPageYOffset;
    previousPageYOffset = pageYOffset;

    if (!mostTopParagraph)
        mostTopParagraph  = document.getElementsByTagName('tr')[0];
    mostTopParagraph = (scrollForward
        ? getTopVisibleFollowingSibling(mostTopParagraph)
        : getTopVisiblePrecedingSibling(mostTopParagraph));

    const storageKey = ['section', sectionId, 'paragraph', 'position'].join('_');
    localStorage.setItem(storageKey, mostTopParagraph.id);
    // console.log(mostTopParagraph);
};
scrollHandler = throttle(scrollHandler, 400);
window.addEventListener('scroll', scrollHandler);

const loadScrollPosition = function() {
    if (!sectionId)
        return;
    const storageKey = ['section', sectionId, 'paragraph', 'position'].join('_');

    const targetElem = document.getElementById(localStorage.getItem(storageKey));
    if (!targetElem)
        return;

    targetElem.scrollIntoView(true);
};
window.addEventListener('load', loadScrollPosition);
