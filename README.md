# The OMERO IMPORTER runs the following processes:

1. [Deconvolution](#deconvolution)
2. [Writing logs](#writing-log)
3. [ChromaticShift](#chromaticshift)
4. [Importing](#importing)

----

## <a name="deconvolution">Deconvolution</a>
Deconvolutionは、顕微鏡の焦点面上下に由来するノイズを除去して焦点面でのよりノイズの少ない画像に処理します。

```
path/to/sample_R3D.dv => path/to/sample_R3D.dv_decon
```

## <a name="writing-log">Writing logs</a>
ここでは、ログファイルの情報をDeconvolution後の画像にメタデータとして書き込む。

|Image file |path/to/sample\_R3D.dv\_decon |
|-----------|------------------------------|
|Log file   |path/to/sample\_R3D.dv.log    |

## <a name="chromaticshift">ChromaticShift</a>
ChromaticShiftは、蛍光波長による焦点距離のごく微量な差異を修正する。

```
path/to/sample_R3D.dv_decon => path/to/sample_R3D.dv_decon.zs
```

## <a name="importing">Importing</a>
最後には上記の処理をされた画像をOMEROサーバーにインポートする。
この際、画像のパーミッションから画像の所有者のアカウントを判別しそのOMEROアカウントのデータとしてインポートする。
