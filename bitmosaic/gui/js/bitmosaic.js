/*! 
  * Copyright 2021 by @bitmosaic <bitmosaic@protonmail.com>
  *
  * bitmosaic.js is part of Bitmosaic.
  *
  * Bitmosaic is free software: you can redistribute it and/or modify
  * it under the terms of the GNU General Public License as published by
  * the Free Software Foundation, either version 3 of the License, or
  * (at your option) any later version.
  *
  * Bitmosaic is distributed in the hope that it will be useful,
  * but WITHOUT ANY WARRANTY; without even the implied warranty of
  * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
  * GNU General Public License for more details.
  *
  * You should have received a copy of the GNU General Public License
  * along with BitmosaicI.  If not, see <https://www.gnu.org/licenses/>. 
  */

const MIN_MARGIN = 0
const MAX_MARGIN = 300
const MIN_BORDER_WIDTH = 0
const MAX_BORDER_WIDTH = 20
const MIN_PALETTE_COLORS = 1
const MAX_PALETTE_COLORS = 50
const MIN_SIZE = 8
const MAX_SIZE = 256  // 192
const MIN_DPI = 72
const MAX_DPI = 4000
const MIN_TESSERA_SIDE = 150
const MAX_TESSERA_SIDE = 600
const LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m", "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z"]
const TABLE = '<tr> \
<td><div class="content frame"></div></td> \
<td><div class="content frame"><span class="frameText">0</span></div></td> \
<td><div class="content frame"><span class="frameText">1</span></div></td> \
<td><div class="content frame"><span class="frameText">2</span></div></td> \
<td><div class="content frame"></div></td> \
</tr> \
<tr> \
<td><div class="content frame"><span class="frameText">0</span></div></td> \
<td><div class="content data"><span class="dataText">b</span></div></td> \
<td><div class="content data"><span class="dataText">i</span></div></td> \
<td><div class="content data"><span class="dataText">t</span></div></td> \
<td><div class="content frame"><span class="frameText">0</span></div></td> \
</tr> \
<tr> \
<td><div class="content frame"><span class="frameText">1</span></div></td> \
<td><div class="content data"><span class="dataText">m</span></div></td> \
<td><div class="content data"><span class="dataText">o</span></div></td> \
<td><div class="content data"><span class="dataText">s</span></div></td> \
<td><div class="content frame"><span class="frameText">1</span></div></td> \
</tr> \
<tr> \
<td><div class="content frame"><span class="frameText">2</span></div></td> \
<td><div class="content data"><span class="dataText">a</span></div></td> \
<td><div class="content data"><span class="dataText">i</span></div></td> \
<td><div class="content data"><span class="dataText">c</span></div></td> \
<td><div class="content frame"><span class="frameText">2</span></div></td> \
</tr> \
<tr> \
<td><div class="content frame"></div></td> \
<td><div class="content frame"><span class="frameText">0</span></div></td> \
<td><div class="content frame"><span class="frameText">1</span></div></td> \
<td><div class="content frame"><span class="frameText">2</span></div></td> \
<td><div class="content frame"></div></td> \
</tr>'
var matchNumbers = /^\d+$/;

function setDemoColor(id, color) {
    demoColor = document.getElementById(id)
    demoColor.style.backgroundColor = color
    demoColor.style.color = color
}

function numberInLimits(value, min, max) {
    var inLimits = true
    try {
        number = Number(value)
        inLimits = (min <= number &&  number <= max)
    }
    catch {
        inLimits = false
    }
    return inLimits
}

function randomNumber(min, max) {  
    return Math.random() * (max - min) + min; 
} 

function randomizeArray(array) {
    for (let i = array.length -1; i > 0; i--) {
        const j = Math.floor(Math.random() * i)
        const temp = array[i]
        array[i] = array[j]
        array[j] = temp
    }
    return array
}

function randomizeBitmosaic() {
    var array = randomizeArray("bitmosaic".split(""))
    var dataElements = document.querySelectorAll(".dataText")
    for (let i=0; i<array.length;i++) {
        dataElements[i].innerText = array[i]
    }
}

function errorMessageCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
}

function isValid(field, match) {
    data = document.getElementById(field).value
    if (data !== "") {
        return match.test(data)
    }
    return false
}


/*
 *
 * SECRET SETUP
 *
 */


function setRandomOrigin() {
    max_col_index = 128
    max_row_index = 128
    if (isValid("content-size-cols", matchNumbers) && isValid("content-size-rows", matchNumbers)) {
        max_col_index = Number(document.getElementById("content-size-cols").value) - 1
        max_row_index = Number(document.getElementById("content-size-rows").value) - 1    
    }
    document.getElementById("secret-origin-col").value = Math.trunc(randomNumber(0, max_col_index))
    document.getElementById("secret-origin-row").value = Math.trunc(randomNumber(0, max_row_index))
}

function setRandomComponents() {
    var components = ""
    var numberOfComponents = randomNumber(3, LETTERS.length - 1)
    var numbers = []
    for (var i = 0; i < LETTERS.length - 1; i++) {
        numbers.push(String(i))
    }
    numbers = randomizeArray(numbers)
    letters = randomizeArray(LETTERS)
    for (var i = 0; i < numberOfComponents; i++ ) {
        components += `${letters[i]}:${numbers[i]} `
    }
    components = components.slice(0, -1);
    document.getElementById("secret-components").value = components
}

function addSecret() {
    document.getElementById("secret-save").disabled = true
    var name = document.getElementById("secret-name").value
    var secret = document.getElementById("secret-data").value
    var originCol = document.getElementById("secret-origin-col").value
    var originRow = document.getElementById("secret-origin-row").value
    var components = document.getElementById("secret-components").value
    eel.add_secret(name, secret, originCol, originRow, components)(addSecretCallback)
}

function addSecretCallback(result) {
    document.getElementById("secret-save").disabled = false
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var ul = document.getElementById("secret-list-inline")
    var li = document.createElement("li");
    li.innerHTML = `<span class=\"tag-item\">${result[2]}
                    <a href="#" class=\"remove-button\" onclick="removeSecret('_${result[2]}_')">x</a></span>`
    ul.appendChild(li);
}

function removeSecret(name) {
    eel.remove_secret(name)(removeSecretCallback)
}

function removeSecretCallback(result) {
    var ul = document.getElementById("secret-list-inline")
    var secrets = ul.getElementsByTagName("li")
    for (let i=0; i< secrets.length; i++) {
        secret = secrets[i]
        if (secret.innerHTML.indexOf(result[2]) !== -1) {
            secret.remove()
            return
        }
    }
}


/*
 *
 * FILE OUTPUTS
 *
 */


function setSaveBitmosaicTextFile() {
    var saveTextFile = document.getElementById("output-bitmosaic-text").checked
    eel.set_save_bitmosaic_text_file(saveTextFile)(errorMessageCallback)
}

function setSaveRecoveryTextFile() {
    var save = document.getElementById("output-recovery-text").checked
    eel.set_save_recovery_txt_file(save)(errorMessageCallback)
}

function setSaveRecoveryImage() {
    var save = document.getElementById("output-recovery-image").checked
    eel.set_save_recovery_card(save)(errorMessageCallback)
}


/*
 *
 * CONTENT SETUP
 *
 */


function setMosaicSize() {
    var cols = document.getElementById("content-size-cols").value
    var rows = document.getElementById("content-size-rows").value
    if (numberInLimits(cols, MIN_SIZE, MAX_SIZE) && numberInLimits(rows, MIN_SIZE, MAX_SIZE)) {
        randomizeBitmosaic()
        eel.set_mosaic_size(cols, rows)(errorMessageCallback)
    }
    else {
        setMosaicSizeCallback([1, "Invalid mosaic size", ""])
    }
}

function setMosaicSizeCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
}

function setMosaicDpi() {
    var dpi = document.getElementById("content-dpi").value
    if (numberInLimits(dpi, MIN_DPI, MAX_DPI)) {
        randomizeBitmosaic()
        eel.set_mosaic_dpi(dpi)(setMosaicDpiCallback)
    }
    else {
        setMosaicDpiCallback([1, "Invalid DPI value", ""])
    }
}

function setMosaicDpiCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
}

function setMosaicTesseraSide() {
    var side = document.getElementById("content-tessera-side").value
    if (numberInLimits(side, MIN_TESSERA_SIDE, MAX_TESSERA_SIDE)) {
        randomizeBitmosaic()
        eel.set_mosaic_tessera_side(side)(setMosaicTesseraSideCallback)
    }
    else {
        setMosaicTesseraSideCallback([1, "Invalid value for tessera side", ""])
    }
}

function setMosaicTesseraSideCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
}

function setMosaicBorderWidth() {
    width = document.getElementById("content-border-width").value
    if (numberInLimits(width, MIN_BORDER_WIDTH, MAX_BORDER_WIDTH)) {
        randomizeBitmosaic()
        eel.set_mosaic_border_width(width)(setMosaicBorderWidthCallback)
    }
    else {
        setMosaicBorderWidthCallback([1, "Invalid border width value", ""])
        document.getElementById("content-border-width").value = 1
    }
}

function setMosaicBorderWidthCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var table = document.getElementById("sample-bitmosaic")
    table.style.borderSpacing = `${width}px`
}

function setMosaicBorderColor() {
    randomizeBitmosaic()
    random = document.getElementById("content-random-border-color").checked
    color = random ? "random" : document.getElementById("content-border-color").value
    eel.set_mosaic_border_color(color)(setMosaicBorderColorCallback)
}

function setMosaicBorderColorCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var input = document.getElementById("content-border-color")
    input.value = result[2]
    setDemoColor("square-content-border-color", result[2])
    var table = document.getElementById("sample-bitmosaic")
    table.style.borderColor = result[2]
    table.style.backgroundColor = result[2]
}

function setMosaicShowCoordinates() {
    randomizeBitmosaic()
    var show = document.getElementById("content-show-coordinates").checked
    eel.set_mosaic_show_coordinates(show)(errorMessageCallback)
}

function mosaicBackgroundTypeChanged() {
    randomizeBitmosaic()
    var option = document.getElementById("content-background-type").value
    var palette = document.getElementById("content-background-type-palette")
    var image = document.getElementById("content-background-type-image")
    if (option == "1") {
        palette.style.display = "block"
        image.style.display = "none"
        document.getElementById("content-background-image-name").innerText = "No image selected"
    }
    else {
        palette.style.display = "none"
        image.style.display = "block"
    }
}

function setMosaicPaletteColors() {
    random = document.getElementById("content-random-background-color").checked
    colors = document.getElementById("content-palette-number-of-colors").value
    baseColor = random ? "random" : document.getElementById("content-background-color").value
    if (numberInLimits(colors, MIN_MARGIN, MAX_MARGIN)) {
        randomizeBitmosaic()
        eel.set_mosaic_palette_colors(baseColor, colors)(setMosaicPaleteColorsCallback)
    }
    else {
        setMosaicPaleteColorsCallback([1, "Invalid number of colors for the palette"])
    }
}

function setMosaicPaleteColorsCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var input = document.getElementById("content-background-color")
    input.value = result[2]
    setDemoColor("square-content-background-color", result[2])
}

function setMosaicBackgroundImage() {
    button = document.getElementById("content-select-background-image")
    var input = document.createElement('input')
    input.type = 'file'
    var validTypes = ["image/jpeg", "image/gif", "image/png"]
    input.onchange = e => {
        button.disabled = true
        var file = e.target.files[0]
        if (validTypes.includes(file.type)) {
            randomizeBitmosaic()
            document.getElementById("content-background-image-name").innerText = file.name
            document.getElementById("content-background-image").src = "bitmosaic_images/" + file.name
            eel.set_mosaic_image(file.name)(setMosaicBackgroundImageCallback)
        }
        else {
            button.disabled = false
            setMosaicBackgroundImageCallback([1, "Invalid file type for mosaic image"])
        }
    }
    input.click()
}

function setMosaicBackgroundImageCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
    document.getElementById("content-select-background-image").disabled = false
}


/*
 *
 * FRAME SETUP
 *
 */


function setFrame() {
    randomizeBitmosaic()
    var frame = document.getElementById("frame-add").checked
    var showIndexes = document.getElementById("frame-show-indexes")
    var textColor = document.getElementById("frame-text-color-row")
    var textColorRandom = document.getElementById("frame-random-text-color")
    var textColorUpdate = document.getElementById("frame-text-color-update")
    var backgroundColor = document.getElementById("frame-background-color-row")
    var backgroundColorRandom = document.getElementById("frame-random-background-color")
    var backgroundColorUpdate = document.getElementById("frame-background-color-update")
    if (frame) {
        showIndexes.disabled = false
        textColor.disabled = false
        textColorRandom.disabled = false
        textColorUpdate.onclick = setFrameTextColor
        backgroundColor.disabled = false
        backgroundColorRandom.disabled = false
        backgroundColorUpdate.onclick = setFrameBackgroundColor
    }
    else {
        showIndexes.disabled = true
        textColor.disabled = true
        textColorRandom.disabled = true
        textColorUpdate.onclick = ""
        backgroundColor.disabled = true
        backgroundColorRandom.disabled = true
        backgroundColorUpdate.onclick = ""
    }
    eel.set_frame(frame)(setFrameCallback)
}

function setFrameCallback(result) {    
    if (result[0] != 0) {
        alert(result[1])
        return
    }

    result = result[2]

    if (!result) {
        rows = document.getElementsByTagName("tr")
        rows[0].remove()
        rows[3].remove()

        var cols_row_0 = rows[0].getElementsByTagName("td")
        cols_row_0[0].remove()
        cols_row_0[3].remove()
        var cols_row_1 = rows[1].getElementsByTagName("td")
        cols_row_1[0].remove()
        cols_row_1[3].remove()
        var cols_row_2 = rows[2].getElementsByTagName("td")
        cols_row_2[0].remove()
        cols_row_2[3].remove()
    }
    else
    {
        document.getElementById("sample-bitmosaic").innerHTML = TABLE
    }

    document.getElementById("frame-background-color").disabled = !result
    document.getElementById("frame-text-color").disabled = !result
}

function setFrameBackgroundColor() {
    randomizeBitmosaic()
    var random = document.getElementById("frame-random-background-color").checked
    var color = random ? "random" : document.getElementById("frame-background-color").value
    eel.set_frame_background_color(color)(setFrameBackgroundColorCallback)
}

function setFrameBackgroundColorCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var input = document.getElementById("frame-background-color")
    input.value = result[2];
    setDemoColor("square-frame-background-color", result[2])
    var frameElements = document.querySelectorAll(".frame")
    frameElements.forEach(element => {
        element.style.backgroundColor = result[2]
    });
}

function setFrameTextVisibility() {
    visible = document.getElementById("frame-show-indexes").checked
    eel.set_frame_text_visibility(visible)(setFrameTextVisibilityCallback)
}

function setFrameTextVisibilityCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var frameElements = document.querySelectorAll(".frameText")
    frameElements.forEach(element => {
        element.style.visibility = result[2] ? "visible" : "hidden"
    });
    document.getElementById("frame-text-color-row").hidden = !result[2]
}

function setFrameTextColor() {
    randomizeBitmosaic()
    random = document.getElementById("frame-random-text-color").checked
    color = random ? "random" : document.getElementById("frame-text-color").value
    eel.set_frame_text_color(color)(setFrameTextColorCallback)
}

function setFrameTextColorCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var input = document.getElementById("frame-text-color")
    input.value = result[2]
    setDemoColor("square-frame-text-color", result[2])
    var frameElements = document.querySelectorAll(".frameText")
    frameElements.forEach(element => {
        element.style.color = result[2]
    });
}


/*
 *
 * MARGIN SETUP
 *
 */


function setMarginColor() {
    randomizeBitmosaic()
    var random = document.getElementById("margin-color-random").checked
    var color = random ? "random" : document.getElementById("margin-color").value
    eel.set_mosaic_background_color(color)(setMarginColorCallback)
}

function setMarginColorCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var input = document.getElementById("margin-color")
    input.value = result[2];
    setDemoColor("square-margin-color", result[2])
    document.getElementById("sample-margin").style.backgroundColor = result[2]
}

function updateMargin() {
    document.getElementById("margin-update").disabled = true
    mTop = document.getElementById("margin-top").value  
    mRight = document.getElementById("margin-right").value
    mBottom = document.getElementById("margin-bottom").value
    mLeft = document.getElementById("margin-left").value
    margin = [mTop, mRight, mBottom, mLeft]

    isValid = true
    margin.forEach(m => {
        isValid = isValid && numberInLimits(m, MIN_MARGIN, MAX_MARGIN)
    })

    if (!isValid) {
        updateMarginCallback([1,"Invalid values for margin",""])
        return
    }

    randomizeBitmosaic()
    document.getElementById("sample-margin").style.padding = `${mTop}px ${mRight}px ${mBottom}px ${mLeft}px`
    eel.set_margin(mTop, mRight, mBottom, mLeft)(updateMarginCallback)
}

function updateMarginCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
    }
    document.getElementById("margin-update").disabled = false
}


/*
 *
 * DATA DOMAIN
 *
 */

function dataDomainTypeChanged() {
    var dataDomainType = document.getElementById('data-domain-type').value
    var dataDomainTypeFile = document.getElementById('data-domain-file')
    var dataDomainTypeRegex = document.getElementById('data-domain-regex')

    if (dataDomainType == "0") {
        dataDomainTypeFile.style.display = "block"
        dataDomainTypeRegex.style.display = "none"
    }
    else {
        dataDomainTypeFile.style.display = "none"
        dataDomainTypeRegex.style.display = "block"
    }
}

function addDataDomainFile() {
    button = document.getElementById("select-domain")
    var input = document.createElement('input')
    input.type = 'file'
    var validTypes = ["text/plain"]
    input.onchange = e => {
        button.disabled = true
        var file = e.target.files[0]
        if (validTypes.includes(file.type)) {
            randomizeBitmosaic()
            eel.add_dictionary_data_domain(file.name)(addDomainCallback)
        }
        else {
            button.disabled = false
            addDomainCallback([1, "Invalid file type for domain data"])
        }
    }
    input.click()
}

function addDataDomainRegex() {
    var regex = document.getElementById("regex").value;
    eel.add_regex_data_domain(regex)(addDomainCallback)
}

function addDomainCallback(result) {
    document.getElementById("select-domain").disabled = false
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    var ul = document.getElementById("domain-list-inline")
    var li = document.createElement("li");
    li.innerHTML = `<span class=\"tag-item\">${result[2]}
                    <a href="#" class=\"remove-button\" onclick="removeDomain('_${result[2]}_')">x</a></span>`
    ul.appendChild(li);
}


function removeDomain(name) {
    eel.remove_data_domain(name)(removeDomainCallback)
}

function removeDomainCallback(result) {
    var ul = document.getElementById("domain-list-inline")
    var domains = ul.getElementsByTagName("li")
    for (let i=0; i< domains.length; i++) {
        domain = domains[i]
        if (domain.innerHTML.indexOf(result[2]) !== -1) {
            domain.remove()
            return
        }
    }
}

/*
 *
 * SECRET RECOVERY
 *
 */


function recoveryTypeChanged() {
    var recoveryType = document.getElementById('recovery-type').value
    var recoveryTypeFile = document.getElementById('file-recovery')
    var recoveryTypeManual = document.getElementById('manual-recovery')
            
    if (recoveryType == "0") {
        recoveryTypeFile.style.display = "block"
        recoveryTypeManual.style.display = "none"
    }
    else {
        recoveryTypeFile.style.display = "none"
        recoveryTypeManual.style.display = "block"
    }
}

function setRecoveryInfoFile() {
    button = document.getElementById("recovery-recovery-select")
    var input = document.createElement('input')
    input.type = 'file'
    var validTypes = ["text/plain"]
    input.onchange = e => {
        var file = e.target.files[0]
        if (validTypes.includes(file.type)) {
            randomizeBitmosaic()
            document.getElementById("recovery-recovery-file").innerText = file.name
        }
    }
    input.click()
}

function setBitmosaicFile() {
    button = document.getElementById("recovery-bitmosaic-select")
    var input = document.createElement('input')
    input.type = 'file'
    var validTypes = ["text/plain"]
    input.onchange = e => {
        var file = e.target.files[0]
        if (validTypes.includes(file.type)) {
            randomizeBitmosaic()
            document.getElementById("recovery-bitmosaic-file").innerText = file.name
        }
    }
    input.click()
}


/*
 *
 * ACTIONS
 *
 */


function createBitmosaic() {
    document.getElementById("create-bitmosaic").disabled = true
    document.getElementById("create-bitmosaic").innerText = "Building..."
    randomizeBitmosaic()
    eel.create_bitmosaic()(createBitmosaicCallback)
}

function createBitmosaicCallback(result) {
    document.getElementById("create-bitmosaic").innerText = "Create bitmosaic"
    document.getElementById("create-bitmosaic").disabled = false
    if (result[0] == 0) {
        alert(result[1] + " " + result[2])
    }
    else {
        alert(result[1])
    }
}

function recoverSecret(){
    randomizeBitmosaic()
    var recoveryType = document.getElementById('recovery-type').value
    var bitmosaicFile = document.getElementById("recovery-bitmosaic-file").innerText
    if (recoveryType == "0") {
        var recoveryInfoFile = document.getElementById("recovery-recovery-file").innerText
        eel.recover_secret_from_file(bitmosaicFile, recoveryInfoFile)(recoverSecretCallback)
    }
    else {
        var cols = document.getElementById("recovery-size-cols").value
        var rows = document.getElementById("recovery-size-rows").value
        if (!numberInLimits(cols, MIN_SIZE, MAX_SIZE) && numberInLimits(rows, MIN_SIZE, MAX_SIZE)) {
            recoverSecretCallback([1, "Invalid recovery size", ""])
        }
        var col = document.getElementById("recovery-origin-col").value
        var row = document.getElementById("recovery-origin-row").value
        var components = document.getElementById("recovery-components").value
        var length = document.getElementById("recovery-length").value
        eel.recover_secret_from_form(bitmosaicFile, cols, rows, col, row, components, length)(recoverSecretCallback)
    }
}

function recoverSecretCallback(result) {
    if (result[0] != 0) {
        alert(result[1])
        return
    }
    document.getElementById("recovery-recovery-file").innerText = "No recovery file selected"
    document.getElementById("recovery-bitmosaic-file").innerText = "No bitmosaic file selected"
    alert(result[1] + result[2])
}