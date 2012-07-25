<?php
$wgHooks['SkinTemplateOutputPageBeforeExec'][] = 'stratumOpenCloseSidebarHook';
function stratumOpenCloseSidebarHook($skin, $tpl) {
  if(isset($tpl->data['sidebar']['Space-Status']))
    $tpl->data['sidebar']['Space-Status'] = '<ul><li><a title="'.
       '&Ouml;ffnungsstatus" href="/wiki/Open/Close-Monitor">'.
       '<img style="border:none; height:2em;" src="http://status.stratum0.org/'.
       'status.png" /></a></li></ul>';
  return true;
}
?>
