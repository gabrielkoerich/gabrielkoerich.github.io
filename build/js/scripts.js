/*!
 * Gabriel Koerich
 * https://gabrielkoerich.github.io
 * @author Gabriel Koerich
 * @version 1.0.0
 * Copyright 2016. MIT licensed.
 */
'use strict';

var pictures = [
  'https://en.gravatar.com/userimage/11625806/8900fbd827e8cefe473336e9c82251da.jpg?size=600',
  'https://en.gravatar.com/userimage/11625806/3a6df0444873d3eb52126312ac0ab901.jpg?size=600',
  'https://en.gravatar.com/userimage/11625806/3a6df0444873d3eb52126312ac0ab901.jpg?size=600',
  // 'https://en.gravatar.com/userimage/11625806/3a6df0444873d3eb52126312ac0ab901.jpg?size=600',
  // 'https://en.gravatar.com/userimage/11625806/3a6df0444873d3eb52126312ac0ab901.jpg?size=600',
  // 'https://en.gravatar.com/userimage/11625806/c29667c3f21dcc852dea802cbb0541d7.jpg?size=600',
  // 'https://en.gravatar.com/userimage/11625806/ae6c42060c038da3a23e46f3877f1e65.jpg?size=600',
  // 'http://graph.facebook.com/100000670444837/picture?width=400&amp;height=400',
  'https://cdn-images-1.medium.com/fit/c/200/200/0*x5dJKz8p5zDWgd0x.jpeg',
  // 'https://cdn-images-1.medium.com/fit/c/200/200/0*x5dJKz8p5zDWgd0x.jpeg',
  'https://pbs.twimg.com/profile_images/558687561149714434/rpXnZ5CS_400x400.jpeg',
  'https://pbs.twimg.com/profile_images/558687561149714434/rpXnZ5CS_400x400.jpeg',
  'https://pbs.twimg.com/profile_images/558687561149714434/rpXnZ5CS_400x400.jpeg',
];

var image = document.createElement('img');
image.src = pictures[Math.floor(Math.random() * pictures.length)];
image.width = '210';
image.alt = '';

document.getElementById('picture').appendChild(image);
