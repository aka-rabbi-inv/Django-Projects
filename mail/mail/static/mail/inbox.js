const show_email = document.createElement('div');
const sender = document.createElement('h6');
const subject = document.createElement('h6');
const recipient_container = document.createElement('div');
const recipients = document.createElement('h6');
const timestamp = document.createElement('h6');
const body = document.createElement('h6');
const reply = document.createElement('button');

document.addEventListener('DOMContentLoaded', function() {

  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  recipient_container.append(recipients, timestamp);
  show_email.append(subject, sender, recipient_container, body);
  document.querySelector('#email-show').append(show_email);
  document.querySelector('#email-show').append(document.createElement('hr'));

  document.querySelector('#compose-form').onsubmit = send_mail;
  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email(recipient='', subject='', body='', time='') {
  if(document.querySelector("#invalid-text") != null){
    document.querySelector("#invalid-text").remove();
  }
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';
  document.querySelector('#email-show').style.display = 'none';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = typeof recipient==="object" ? '':recipient;

  if (subject){
    if(subject.startsWith('Re:')){
      document.querySelector('#compose-subject').value = subject;
    }
    else{
      document.querySelector('#compose-subject').value = "Re: "+subject;
    }
  }
  else{
    document.querySelector('#compose-subject').value = "";
  }
  
  document.querySelector('#compose-body').value = body ? `On ${time}, ${recipient} wrote:\n`+">>> "+body+"\n>>> ":'';

  
}

function load_mailbox(mailbox) {
  document.querySelector('#archive-btn').style.display = mailbox==='sent' ? "none":"block";
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-show').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;
  
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    emails.forEach(email => {

      const email_div = document.createElement('div');
      email_div.onclick = () => view_mail(email);
      // document.querySelector('#archive-btn').onclick = () => archive_mail(email);
      // email_div.setAttribute("onclick", `view_mail("aaaa")` );
      // email_div.setAttribute("href", "#");
      email_div.setAttribute("class", "email-div"); // shadow p-3 mb-2 rounded 
    

      const sender = document.createElement('h6');
      const subject = document.createElement('h6');
      const time = document.createElement('h6');

      sender.innerHTML = email["sender"];
      subject.innerHTML = email["subject"].length > 56 ? email["subject"].substring(0, 10)+ "...": email["subject"];
      time.innerHTML = email["timestamp"];

      document.querySelector('#emails-view').append(document.createElement('hr'));

      email_div.append(sender, subject, time);
      
      document.querySelector('#emails-view').append(email_div);

      if(email.read === true){
        email_div.style.backgroundColor = "#E8E8E8";
        email_div.childNodes.forEach( node => {
          node.style.fontWeight = "400";
        });
      }
      
      document.querySelector('#emails-view').append(document.createElement('hr'));
    });
  });

}

function send_mail(){

  fetch('/emails', {
    method:"POST",
    body: JSON.stringify({
      recipients: document.querySelector('#compose-recipients').value,
      subject: document.querySelector('#compose-subject').value,
      body: document.querySelector('#compose-body').value,
    })
  })
  .then(response => {

    if (response.status === 201){ load_mailbox('sent'); }
    else if (response.status === 400) { 
      compose_email();
      const invalid_recipient = document.createElement('h6');
      invalid_recipient.setAttribute("id", "invalid-text");
      invalid_recipient.innerHTML = "invalid user";
      document.querySelectorAll('.form-group')[1].append(invalid_recipient);
     }
    
  });

  return false;
}

function view_mail(email){
  document.querySelector('#archive-btn').innerHTML = email.archived ? "Unarchive":"Archive";
  fetch(`/emails/${email.id}`, {
    method:"PUT",
    body: JSON.stringify({
      read: true
    })
  })
  .then(response => {
    // console.log(email.id,email.archived);
  });
  
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-show').style.display = 'flex';

  document.querySelector('#archive-btn').onclick = () =>{
    fetch(`/emails/${email.id}`, {
      method:"PUT",
      body: JSON.stringify({
        archived: !email.archived
      })
    })
    .then(response => {
      if(response.status === 204){
        load_mailbox('inbox');
      }
    });
    var button_text = document.querySelector('#archive-btn');
    button_text.innerHTML = button_text.innerHTML==="Archive" ? "Unarchive":"Archive"; 
    
  }


  sender.innerHTML = email["sender"];
  recipients.innerHTML = "to " + email["recipients"];
  subject.innerHTML = email["subject"];
  subject.setAttribute("class", "display-4");
  timestamp.innerHTML = email["timestamp"];
  body.innerHTML = email["body"];
  body.style.whiteSpace = "pre-wrap";
  body.style.fontWeight = "400";
  recipient_container.setAttribute("class", "recipients");


  reply.innerHTML = "reply";
  reply.onclick = () =>{
    compose_email(sender.innerHTML, subject.innerHTML, body.innerHTML, timestamp.innerHTML);
  };
  reply.setAttribute("id", "reply-btn");
  document.querySelector('#email-show').append(reply);
  return false;
}



// window.onbeforeunload = function() { return false; };