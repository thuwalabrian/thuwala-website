// Small homepage interactions: testimonial carousel
document.addEventListener('DOMContentLoaded', function(){
  try{
    const carousel = document.querySelector('.testimonials-carousel');
    if(!carousel) return;
    const items = Array.from(carousel.querySelectorAll('.testimonial'));
    if(items.length <= 1) return;

    let index = 0;
    const rotate = () => {
      items.forEach((it,i)=>{
        it.style.transform = `translateX(${(i - index) * 100}%)`;
      });
      index = (index + 1) % items.length;
    };

    // initialize positions
    items.forEach((it,i)=> it.style.transform = `translateX(${i * 100}%)`);
    // autoplay every 5s
    let timer = setInterval(rotate, 5000);

    // pause on hover
    carousel.addEventListener('mouseenter', ()=> clearInterval(timer));
    carousel.addEventListener('mouseleave', ()=> timer = setInterval(rotate, 5000));
  }catch(e){console.error('homepage.js', e)}
});
