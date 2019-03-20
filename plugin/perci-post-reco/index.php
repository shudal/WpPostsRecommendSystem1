<?php
/*
 * Plugin Name: 文章推荐
 * Description: 根据用户游览历史推荐文章。
 * Author: Junhao
 * Version: 1.0
 */

add_action('perci_post_reco', 'perci_postreco_record');
function perci_postreco_record($arg) {
	try {
		$userid = $arg['userid'];
		$postid = $arg['postid'];
    	$user_have_viewed = get_user_meta($userid, '_perci_haku_viewed')[0];
    	update_user_meta($userid, '_perci_haku_viewed', $user_have_viewed."|".$postid);

	} catch (\Exception $e) {

	}
}
