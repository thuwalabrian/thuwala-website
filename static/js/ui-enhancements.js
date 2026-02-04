// Lightweight UI enhancements: smooth scroll, focus outlines, simple page fade
(function(){
    'use strict';

    // Smooth scroll for anchors (progressive enhancement)
    function enableSmoothScroll(){
        if('scrollBehavior' in document.documentElement.style) return; // native
        document.querySelectorAll('a[href^="#"]').forEach(function(a){
            a.addEventListener('click', function(e){
                var target = document.querySelector(a.getAttribute('href'));
                if(target){
                    e.preventDefault();
                    var top = target.getBoundingClientRect().top + window.pageYOffset - 20;
                    window.scrollTo({ top: top, behavior: 'smooth' });
                }
            });
        });
    }

    // Add subtle page transition on load
    function pageFadeIn(){
        try{
            document.documentElement.classList.add('ui-fade-enter');
            window.requestAnimationFrame(function(){
                document.documentElement.classList.add('ui-fade-enter-active');
                document.documentElement.classList.remove('ui-fade-enter');
            });
        }catch(e){}
    }

    // Improve focus outlines for keyboard users
    function initFocusStyles(){
        function handleFirstTab(e){
            if(e.key === 'Tab'){
                document.documentElement.classList.add('user-is-tabbing');
                window.removeEventListener('keydown', handleFirstTab);
            }
        }
        window.addEventListener('keydown', handleFirstTab);
    }

    document.addEventListener('DOMContentLoaded', function(){
        enableSmoothScroll();
        pageFadeIn();
        initFocusStyles();
    });
})();
