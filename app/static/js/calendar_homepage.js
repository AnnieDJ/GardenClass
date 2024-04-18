document.addEventListener('DOMContentLoaded', function() {
    var calendarEl = document.getElementById('calendar');

    var calendar = new FullCalendar.Calendar(calendarEl, {
        timeZone: 'UTC',
        initialView: 'dayGridMonth',
        events: '/get_workshop_mainpage',
        editable: true,
        selectable: true,
        headerToolbar: {
            left: 'prev,next today',
            center: 'title',
            right: 'dayGridMonth,timeGridWeek,timeGridDay'
        },

        eventClick: function(info) {
          var eventTitle = info.event.title;
          var eventStart = info.event.start;
          var eventEnd = info.event.end;
          var eventCourseId = info.event.extendedProps.course_id;
          var eventType = info.event.extendedProps.type;
          var eventAddress = info.event.extendedProps.location;
          var eventInstructor = info.event.extendedProps.instructor;
      
          var modalTitle = document.getElementById('modal-title');
          modalTitle.innerHTML = eventTitle;
      
          var modalBody = document.getElementById('modal-body');
          modalBody.innerHTML = `
              <p>Start: ${eventStart}</p>
              <p>End: ${eventEnd}</p>
              <p>Course Id: ${eventCourseId}</p>
              <p>Type: ${eventType}</p>
              <p>Location: ${eventAddress}</p>
              <p>Instructor: ${eventInstructor}</p>
          `;
      
          var modal = document.getElementById('myModal');
          modal.style.display = 'block';
      }
      
      
    });

    calendar.render();
});

function closeModal() {
  var modal = document.getElementById('myModal');
  modal.style.display = 'none';
}