function validateForm() {
  // test si vide nomComplet
  var input = document.getElementById("nomComplet");
  var value = input.value.trim();

  if (value.length === 0) {
      champVidenomComplet.style.display = "inline";
      input.style.border = "1px solid red";
  } else {
      champVidenomComplet.style.display = "none";
      input.style.border = "1px solid #ccc";
  }
    // test si vide username
    var input = document.getElementById("sai_username");
    var value = input.value.trim();

    if (value.length === 0) {
        champVidesai_username.style.display = "inline";
        input.style.border = "1px solid red";
    } else {
        champVidesai_username.style.display = "none";
        input.style.border = "1px solid #ccc";
    }
    // email error
    var emailInput = document.getElementById("sai_email");
    var emailError = document.getElementById("email-error");
    var emailPattern = /([^.@]+)(\.[^.@]+)*@([^.@]+\.)+([^.@]+)/;
    var emailValue = emailInput.value;
    if (!emailPattern.test(emailValue)) {
        emailError.style.display = "inline";
        emailInput.style.border = "1px solid red";
        emailInput.value = "";
        return false;
      } else {
        emailError.style.display = "none";
        emailInput.style.border = "1px solid #ccc";
        emailInput.value = emailValue;
      }
    //mdp error
    var mdpInput = document.getElementById("sai_password");
    var mdpPattern = /^(?=.*[a-z])(?=.*[A-Z]).{8,}$/;
    var mdpError = document.getElementById("mdp-error");
    
    var mdpValue = mdpInput.value;
    
    if (!mdpPattern.test(mdpValue)) {
        mdpError.style.display = "inline";
        mdpInput.style.border = "1px solid red";
        mdpInput.value = "";
      return false;
    } else {
        mdpError.style.display = "none";
        mdpInput.style.border = "1px solid #ccc";
      mdpInput.value = mdpValue;
    }
    return true;
  }