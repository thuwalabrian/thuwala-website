// Admin UI enhancements: simple client-side validation and nicer submit states
(function(){
    'use strict';

    document.addEventListener('DOMContentLoaded', function(){
        document.querySelectorAll('form').forEach(function(form){
            form.addEventListener('submit', function(e){
                // Only basic validation: required fields
                var invalid = false;
                form.querySelectorAll('[required]').forEach(function(inp){
                    if(!inp.value || inp.value.trim() === ''){
                        invalid = true;
                        inp.classList.add('input-invalid');
                    } else {
                        inp.classList.remove('input-invalid');
                    }
                });

                if(invalid){
                    e.preventDefault();
                    var first = form.querySelector('.input-invalid');
                    if(first) first.focus();
                } else {
                    // show subtle loading state if submit button exists
                    var btn = form.querySelector('button[type=submit], input[type=submit]');
                    if(btn){
                        btn.dataset.orig = btn.innerHTML;
                        btn.disabled = true;
                        btn.innerHTML = '<span class="loading" aria-hidden="true"></span> Processing...';
                    }
                }
            });
        });
    });
})();
