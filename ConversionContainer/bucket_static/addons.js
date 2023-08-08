let create_favicon = () => {
  let favicon32 = document.createElement('link');
  favicon32.rel = 'icon';
  favicon32.type = 'image/png';
  favicon32.href = 'https://static.arxiv.org/static/browse/0.3.4/images/icons/favicon-32x32.png';
  favicon32.sizes = '32x32';

  let favicon16 = document.createElement('link');
  favicon16.rel = 'icon';
  favicon16.type = 'image/png';
  favicon16.href = 'https://static.arxiv.org/static/browse/0.3.4/images/icons/favicon-16x16.png';
  favicon16.sizes = '16x16';

  document.head.append([favicon16, favicon32])
}

let create_header = () => {
    let header = document.createElement('header');
    let ABS_URL_BASE = 'https://arxiv.org/abs';
    let id = window.location.pathname.split('/')[2];
    // if (id === 'submission') {
    //     header.innerHTML =
    //     '<a href="#main" class="skip">Skip to main content</a> \
    //     <img src="https://services.dev.arxiv.org/html/arxiv-logo-one-color-white.svg" alt="logo" role="presentation" class="logo"> \
    //     <img src="https://services.dev.arxiv.org/html/arxiv-logomark-small-white.svg" alt="logo" role="presentation" class="logomark"> \
    //     <div role="banner" class="header-message"> \
    //         <strong>Experimental HTML</strong>.Use Alt+Y to enable accessible section reporting links and Alt+Shift+Y to disable. \
    //     </div> \
    //     <div></div>';
    // } else {
    //     header.innerHTML =
    //     `<a href="#main" class="skip">Skip to main content</a> \
    //     <img src="https://services.dev.arxiv.org/html/arxiv-logo-one-color-white.svg" alt="logo" role="presentation" class="logo"> \
    //     <img src="https://services.dev.arxiv.org/html/arxiv-logomark-small-white.svg" alt="logo" role="presentation" class="logomark"> \
    //     <div role="banner" class="header-message"> \
    //         <strong>Experimental HTML</strong>. Report rendering errors with the "Open Issue" button. <a href="#footer">Reference all keyboard commands</a> in the footer. \
    //     </div>`;
    // }

    var LogoBanner = document.createElement('div');

    // Create full size logo for desktop
    var logoImage = document.createElement('img');
    logoImage.alt = 'logo';
    logoImage.className = 'logo';
    logoImage.setAttribute('role', 'presentation');
    logoImage.style.backgroundColor = 'transparent';
    logoImage.src = "https://services.dev.arxiv.org/html/arxiv-logo-one-color-white.svg";

    // Create logomark image for mobile
    var logomarkImage = document.createElement('img');
    logomarkImage.alt = 'logo';
    logomarkImage.className = 'logomark';
    logomarkImage.setAttribute('role', 'presentation');
    logomarkImage.style.backgroundColor='transparent'
    logomarkImage.src = 'https://services.dev.arxiv.org/html/arxiv-logomark-small-white.svg';

    // Create header message
    var headerMessage = document.createElement('div');
    headerMessage.className = 'header-message';
    headerMessage.setAttribute('role', 'banner');
    headerMessage.style.paddingLeft='15px';
    headerMessage.style.paddingTop='5px';
    if (id === 'submission') {
        headerMessage.innerHTML = 'This is <strong>Experimental HTML</strong>. By design, HTML will not look exactly like the PDF. We invite you to report any errors that don\'t represent the intent or meaning of your paper. <span class="sr-only">Use Alt+Y to enable accessible section reporting links and Alt+Shift+Y to disable.</span>'
    }else{
        headerMessage.innerHTML = 'This is <strong>Experimental HTML</strong>. We invite you to report rendering errors. <span class="sr-only">Use Alt+Y to toggle on accessible reporting links and Alt+Shift+Y to toggle off.</span>'
    }

    LogoBanner.appendChild(logoImage);
    LogoBanner.appendChild(logomarkImage);
    LogoBanner.appendChild(headerMessage);
    LogoBanner.style.display = 'flex';
    LogoBanner.style.width = '60%';

    var Links = document.createElement('div');

    var commandLink = document.createElement('a');
    commandLink.setAttribute('class', 'ar5iv-footer-button hover-effect');
    commandLink.style.color = 'white'
    commandLink.href = "#footer";
    commandLink.textContent = 'Keyboard Commands';

    var issueLink = document.createElement('a');
    issueLink.setAttribute('class', 'ar5iv-footer-button hover-effect');
    issueLink.setAttribute('target', '_blank');
    issueLink.style.color = 'white'
    issueLink.textContent = 'Open Issue';
    issueLink.href = '#myForm';
    issueLink.addEventListener('click', function(event) {
        event.preventDefault();
        var modal = document.getElementById('myForm');
        modal.style.display = 'block';
        bugReportState.setInitiateWay("Header");
      });

    var night = document.createElement('a');
    night.setAttribute('class', 'ar5iv-toggle-color-scheme');
    night.setAttribute('href', 'javascript:toggleColorScheme()');
    night.setAttribute('title', 'Toggle ar5iv color scheme');
    var nightSpan = document.createElement('span');
    nightSpan.setAttribute('class', 'color-scheme-icon');
    night.appendChild(nightSpan);
    night.style.float = 'right'

    Links.appendChild(commandLink);
    Links.appendChild(issueLink);
    Links.appendChild(night);
    Links.style.display = 'inline-flex';
    Links.style.alignItems = 'center';

    document.body.insertBefore(header, document.body.firstChild);
    header.appendChild(LogoBanner)
    header.appendChild(Links)
}

let create_footer = () => {
    let footer = document.createElement('footer');
    let ltx_page_footer = document.createElement('div');
    footer.setAttribute('id', 'footer');
    footer.setAttribute('class', 'ltx_document');
    footer.innerHTML =
    '<div class="keyboard-glossary ltx_page_content"> \
        <h2>Keyboard commands and instructions for reporting errors</h2> \
        <p>HTML versions of papers are experimental and a step towards improving accessibility and mobile device support. We appreciate feedback on errors in the HTML that will help us improve the conversion and rendering. Use the methods listed below to report errors:</p> \
        <ul> \
            <li>Use the "Open Issue" button.</li> \
            <li>To open the report feedback form via keyboard, use "<strong>Ctrl + ?</strong>".</li> \
            <li>You can make a text selection and use the "Open Issue for Selection" button that will display near your cursor.</li> \
            <li class="sr-only">You can use Alt+Y to toggle on and Alt+Shift+Y to toggle off accessible reporting links at each section.</li> \
        </ul> \
        <p>We appreciate your time reviewing and reporting rendering errors in the HTML. It will help us improve the HTML versions for all readers and make papers more accessible, because disability should not be a barrier to accessing the research in your field.</p> \
    </div>';

    var night = document.createElement('a');
    night.setAttribute('class', 'ar5iv-toggle-color-scheme');
    night.setAttribute('href', 'javascript:toggleColorScheme()');
    night.setAttribute('title', 'Toggle ar5iv color scheme');

    var nightSpan = document.createElement('span');
    nightSpan.setAttribute('class', 'color-scheme-icon');
    night.appendChild(nightSpan);

    // Create the second link with class "ar5iv-footer-button" for "Copyright"
    var copyLink = document.createElement('a');
    copyLink.setAttribute('class', 'ar5iv-footer-button');
    copyLink.setAttribute('href', 'https://arxiv.org/help/license');
    copyLink.setAttribute('target', '_blank');
    copyLink.appendChild(document.createTextNode('Copyright'));

    // Create the third link with class "ar5iv-footer-button" for "Privacy Policy"
    var policyLink = document.createElement('a');
    policyLink.setAttribute('class', 'ar5iv-footer-button');
    policyLink.setAttribute('href', 'https://arxiv.org/help/policies/privacy_policy');
    policyLink.setAttribute('target', '_blank');
    policyLink.appendChild(document.createTextNode('Privacy Policy'));

    var HTMLLink = document.createElement('a');
    HTMLLink.setAttribute('class', 'ar5iv-footer-button');
    HTMLLink.setAttribute('href', 'https://info.arxiv.org/about/accessible_HTML.html');
    HTMLLink.setAttribute('target', '_blank');
    HTMLLink.appendChild(document.createTextNode('Why HTML?'));

    var TimeLogo = document.createElement('div');
    TimeLogo.setAttribute('class','ltx_page_logo');
    // Create the timestamp
    var timestamp = document.createTextNode('Generated on Wed Dec 14 18:01:44 2022 by ');
    TimeLogo.appendChild(timestamp);

    var logoLink = document.createElement('a');
    logoLink.href = 'https://math.nist.gov/~BMiller/LaTeXML/';
    logoLink.setAttribute('class','ltx_LaTeXML_logo');

    var logoSpan1 = document.createElement('span');
    logoSpan1.style.letterSpacing = '-0.2em';
    logoSpan1.style.marginRight = '0.1em';

    var letterL = document.createTextNode('L');
    logoSpan1.appendChild(letterL);

    var letterA = document.createElement('span');
    letterA.style.fontSize = '70%';
    letterA.style.position = 'relative';
    letterA.style.bottom = '2.2pt';
    letterA.appendChild(document.createTextNode('A'));
    logoSpan1.appendChild(letterA);

    var letterT = document.createTextNode('T');
    logoSpan1.appendChild(letterT);

    var letterE = document.createElement('span');
    letterE.style.position = 'relative';
    letterE.style.bottom = '-0.4ex';
    letterE.appendChild(document.createTextNode('E'));
    logoSpan1.appendChild(letterE);

    var logoSpan2 = document.createElement('span');
    logoSpan2.setAttribute('class', 'ltx_font_smallcaps');
    logoSpan2.appendChild(document.createTextNode('xml'));

    var logoImage = document.createElement('img');
    logoImage.alt = '[LOGO]';
    logoImage.src = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAsAAAAOCAYAAAD5YeaVAAAAAXNSR0IArs4c6QAAAAZiS0dEAP8A/wD/oL2nkwAAAAlwSFlzAAALEwAACxMBAJqcGAAAAAd0SU1FB9wKExQZLWTEaOUAAAAddEVYdENvbW1lbnQAQ3JlYXRlZCB3aXRoIFRoZSBHSU1Q72QlbgAAAdpJREFUKM9tkL+L2nAARz9fPZNCKFapUn8kyI0e4iRHSR1Kb8ng0lJw6FYHFwv2LwhOpcWxTjeUunYqOmqd6hEoRDhtDWdA8ApRYsSUCDHNt5ul13vz4w0vWCgUnnEc975arX6ORqN3VqtVZbfbTQC4uEHANM3jSqXymFI6yWazP2KxWAXAL9zCUa1Wy2tXVxheKA9YNoR8Pt+aTqe4FVVVvz05O6MBhqUIBGk8Hn8HAOVy+T+XLJfLS4ZhTiRJgqIoVBRFIoric47jPnmeB1mW/9rr9ZpSSn3Lsmir1fJZlqWlUonKsvwWwD8ymc/nXwVBeLjf7xEKhdBut9Hr9WgmkyGEkJwsy5eHG5vN5g0AKIoCAEgkEkin0wQAfN9/cXPdheu6P33fBwB4ngcAcByHJpPJl+fn54mD3Gg0NrquXxeLRQAAwzAYj8cwTZPwPH9/sVg8PXweDAauqqr2cDjEer1GJBLBZDJBs9mE4zjwfZ85lAGg2+06hmGgXq+j3+/DsixYlgVN03a9Xu8jgCNCyIegIAgx13Vfd7vdu+FweG8YRkjXdWy329+dTgeSJD3ieZ7RNO0VAXAPwDEAO5VKndi2fWrb9jWl9Esul6PZbDY9Go1OZ7PZ9z/lyuD3OozU2wAAAABJRU5ErkJggg==';
    logoLink.appendChild(logoSpan1);
    logoLink.appendChild(logoSpan2);
    logoLink.appendChild(logoImage);
    TimeLogo.appendChild(logoLink);

    document.body.appendChild(ltx_page_footer);
    document.body.appendChild(footer);
    //footer.appendChild(ltx_page_footer);
    ltx_page_footer.appendChild(night)
    ltx_page_footer.appendChild(copyLink)
    ltx_page_footer.appendChild(policyLink)
    ltx_page_footer.appendChild(HTMLLink)
    ltx_page_footer.appendChild(TimeLogo)
    ltx_page_footer.setAttribute('class', 'ltx_page_footer');
}

document.addEventListener("DOMContentLoaded", () => {
    create_favicon();
    create_header();
    create_footer();
});

document.addEventListener("DOMContentLoaded", function() {
    const referenceItems = document.querySelectorAll(".ltx_bibitem");
  
    referenceItems.forEach(item => {
      const referenceId = item.getAttribute("id");
      const backToReferenceBtn = document.createElement("button");
      backToReferenceBtn.textContent = "Back to Article";
      backToReferenceBtn.classList.add("back-to-reference-btn");
  
      let scrollPosition = 0;
      let clickedCite = false;
  
      backToReferenceBtn.addEventListener("click", function() {
        if (clickedCite) {
          window.scrollTo(0, scrollPosition);
        } else {
          const citeElement = document.querySelector(`cite a[href="#${referenceId}"]`);
          if (citeElement) {
            citeElement.scrollIntoView({ behavior: "smooth" });
          }
        }
      });
  
      const citeElements = document.querySelectorAll(`cite a[href="#${referenceId}"]`);
      citeElements.forEach(citeElement => {
        citeElement.addEventListener("click", function() {
          scrollPosition = window.scrollY;
          clickedCite = true;
        });
      });
  
      item.insertBefore(backToReferenceBtn, item.firstChild);
    });
  });
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  
  


  