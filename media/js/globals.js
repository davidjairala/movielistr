// Timer to hide info
var timerInf = "";

// Shows the modal window
function showInfo(txt, hide) {
	$('#info').html('<div class="right small">[<a href="#" onclick="hideInfo(); return false;">close</a>]</div>' + txt);
	$('#info').centerInClient();
	$('#info').css('display', 'block');
	if(hide) {
		timerInf = setTimeout("hideInfo()", 3000);
	}
}

// Hides the modal window
function hideInfo() {
	$('#info').html('<!-- i -->');
	$('#info').css('display', 'none');
	timerInf = "";
}

// Adds or removes a friend
function toggleFriend(user_id) {
	// Reset timer in case it's ticking
	timerInf = "";
	$.post('/friends/' + user_id + '/', function(msg) {
		if(msg == 'added') {
			showInfo('The user has been added to your friends list.', true);
			$('#text_friend_' + user_id).html('is your friend.  <a href="#" onclick="toggleFriend(' + user_id + '); return false;">Remove?</a>');
		} else if(msg == 'removed') {
			showInfo('The user has been removed from your friends list.', true);
			$('#text_friend_' + user_id).html('is <strong>not</strong> your friend.  <a href="#" onclick="toggleFriend(' + user_id + '); return false;">Add?</a>');
		} else if(msg == 'err_login') {
			showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to add or remove a friend.', false);
		} else {
			showInfo('An error has occurred, please try again.', false);
		}
	});
}

// Shows a movie's options
function moviesOptions() {
	$('.movie_box').mouseover(function() {
		$(this).css('border', '1px solid orange');
		$(this).find('.add').css('visibility', 'visible');
	});
	$('.movie_box').mouseout(function() {
		$(this).css('border', '1px solid #666666');
		$(this).find('.add').css('visibility', 'hidden');
	});
	$('.movie_box_already_added').mouseover(function() {
		$(this).css('border', '1px solid orange');
		$(this).find('.add').css('visibility', 'visible');
	});
	$('.movie_box_already_added').mouseout(function() {
		$(this).css('border', '1px solid #666666');
		$(this).find('.add').css('visibility', 'hidden');
	});
}

// Removes movie from wishlist
function removeMovieFromWishlist(movie_id) {
	// Reset timer in case it's ticking
	timerInf = "";
	showInfo('Removing...', false);
	$.post('/library/remove_movie_wishlist/' + movie_id + '/', function(msg) {
		if(msg == 'err_login') {
			showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to remove a movie from your wish list.', false);
		} else if(msg == 'alr') {
			showInfo('You have not added this movie to your wish list.', true);
		} else if(msg == 'no_movie') {
			showInfo('You have not selected a movie.', true);
		} else {
			showInfo('The movie has been removed from your wish list.', true);
			$('#movie_img_favorite_' + movie_id).attr('src', '/site_media/imgs/favorite_off_16.png');
		}
	});
}

// Adds movie to wishlist
function addMovieToWishlist(movie_id) {
	// Reset timer in case it's ticking
	timerInf = "";
	showInfo('Adding...', false);
	$.post('/library/add_movie_wishlist/' + movie_id + '/', function(msg) {
		if(msg == 'err_login') {
			showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to add a movie to your wish list.', false);
		} else if(msg == 'alr') {
			showInfo('You have already added this movie to your wish list.', true);
		} else if(msg == 'no_movie') {
			showInfo('You have not selected a movie.', true);
		} else {
			showInfo('The movie has been added to your wish list.', true);
			$('#movie_img_favorite_' + movie_id).attr('src', '/site_media/imgs/favorite_16.png');
		}
	});
}

// Adds a movie to a library
function addMovieToLibrary(movie_id) {
	// Reset timer in case it's ticking
	timerInf = "";
	showInfo('Adding...', false);
	$.post('/library/add_movie/' + movie_id + '/', function(msg) {
		if(msg == 'err_login') {
			showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to add a movie to your library.', false);
		} else if(msg == 'alr') {
			showInfo('You have already added this movie to your library.', true);
		} else if(msg == 'no_movie') {
			showInfo('You have not selected a movie.', true);
		} else {
			showInfo(msg, false);
			$('#add_movie_form').submit(function() {
				var tags = $('#add_movie_tags').val();
				if(tags != '') {
					showInfo('Adding...', false);
					$.post('/library/add_movie/' + movie_id + '/', { tags: tags }, function(msg) {
						if(msg == 'alr') {
							showInfo('You have already added this movie to your library.', true);
						} else if(msg == 'err_login') {
							showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to add a movie to your library.', false);
						} else if(msg == 'ok') {
							showInfo('The movie has been added to your library.', true);
							$('#boxxed_movie_' + movie_id).css('background-color', '#ddffdd');
						}
					});
				} else {
					alert('Please describe where you have stored the movie.');
				}
				return false;
			});
			// Auto focus
			$('#add_movie_tags').focus();
			// Autocomplete de concepto
			$("#add_movie_tags").autocomplete('/ac_tags', {
				multiple: true,
				autoFill: true
			});
		}
	});
}

// Starts location edit
function initEditLocation() {
	$("#edit_movie_tags").autocomplete('/ac_tags', {
		multiple: true,
		autoFill: true
	});
}

// Removes a movie from a library
function removeMovieFromLibrary(movie_id) {
	// Reset timer in case it's ticking
	timerInf = "";
	showInfo('Removing...', false);
	$.post('/library/remove_movie/' + movie_id + '/', function(msg) {
		if(msg == 'err_login') {
			showInfo('You need to <a href="/login">log in</a> or <a href="/register">register</a> to remove a movie from your library.', false);
		} else if(msg == 'no_movie') {
			showInfo('You have not selected a movie.', true);
		} else {
			showInfo('The movie has been removed from your library.', true);
			$('#boxxed_movie_' + movie_id).css('background-color', '#ffcccc');
		}
	});
}

// Shows or hides the related box
function toggleRels() {
	if($('#cont_rels').css('display') == 'none') {
		$('#cont_rels').css('display', 'block');
		$('#cont_rels_link').html('- Similar movies');
	} else {
		$('#cont_rels').css('display', 'none');
		$('#cont_rels_link').html('+ Similar movies');
	}
}

// Shows or hides the trailer box
function toggleTrailer() {
	if($('#cont_trailer').css('display') == 'none') {
		$('#cont_trailer').css('display', 'block');
		$('#cont_trailer_link').html('- Trailer');
	} else {
		$('#cont_trailer').css('display', 'none');
		$('#cont_trailer_link').html('+ Trailer');
	}
}

// On load
$(document).ready(function() {
	moviesOptions();
});