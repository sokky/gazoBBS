<%!
	from gazobbs import conf
%>
% if not res == 0:
<a href="/${conf.SELF_NAME}">[掲示板に戻る]</a>
<table width='100%'>
	<tr>
		<th bgcolor="#e04000">
			<font color="#FFFFFF">レス送信モード</font>
		</th>
	</tr>
</table>
% endif

% if 'admin' in request.session:
<h4>タグがつかえます</h4>
% endif

<center>
<form action="/regist" method="POST" enctype="multipart/form-data">
<input type="hidden" name="mode" value="regist">

% if 'admin' in request.session:
<input type=hidden name=admin value="${conf.ADMIN_PASS}">
% endif

<input type=hidden name="MAX_FILE_SIZE" value="${conf.MAX_KB * 1024}">

% if not res == 0:
<input type="hidden" name="resto" value="${res}">
% endif


<table cellpadding=1 cellspacing=1>
	<tr>
		<td bgcolor="#eeaa88"><b>おなまえ</b></td>
		<td><input type="text" name="name" size="28"></td>
	</tr>
	<tr>
		<td bgcolor="#eeaa88"><b>E-mail</b></td>
		<td><input type="text" name="email" size="28"></td>
	</tr>
	<tr>
		<td bgcolor="#eeaa88"><b>題　　名</b></td>
		<td><input type="text" name="sub" size="35"><input type="submit" value="送信する"></td>
	</tr>
	<tr>
		<td bgcolor="#eeaa88"><b>コメント</b></td>
		<td><textarea name="com" cols="48" rows="4" wrap="soft"></textarea></td>
	</tr>


% if conf.RESIMG or not res == 0:
	<tr>
		<td bgcolor="#eeaa88"><b>添付File</b></td>
		<td><input type="file" name="upfile" size="35">
		[<label><input type="checkbox" name="textonly" value=on>画像なし</label>]</td>
	</tr>
% endif

	<tr>
		<td bgcolor="#eeaa88"><b>削除キー</b></td>
		<td><input type="password" name="pwd" size=8 maxlength=8 value=""><small>(記事の削除用。英数字で8文字以内)</small></td>
	</tr>
	<tr>
		<td colspan=2>
		<small>
		<LI>添付可能ファイル：GIF, JPG, PNG ブラウザによっては正常に添付できないことがあります。
		<LI>最大投稿データ量は ${conf.MAX_KB} KB までです。sage機能付き。
		<LI>画像は横 ${conf.MAX_W}ピクセル、縦 ${conf.MAX_H}ピクセルを超えると縮小表示されます。
		</small>
		</td>
	</tr>
</table>
</form>
</center>
%if request.session.peek_flash():
	%for m in request.session.pop_flash():
	<B>${m}</B>
	%endfor
%endif
<hr>