close all;
clear all;


nsiz=[512,512];

dirCFG='/home/ar/data/append_ageissl_numissl_firstissl_firstage_v2';
dirINP='/mnt/AE822A3E822A0B81/out_PTD2';
dirOUT='/mnt/AE822A3E822A0B81/out_PTD2-resiz';

tptd='PTD2';

fcsvNUM=sprintf('%s/lst_numissl_%s.txt',dirCFG,tptd);

csvNUM=textread(fcsvNUM, '%s');
numNUM=numel(csvNUM);
dataNUM=zeros(numNUM,1);
for ii=1:numNUM
    tnum=str2num(csvNUM{ii});
    dataNUM(ii)=tnum;
end


% % % % % % % % % % % % % % % % % % % % % 
for nn=1:numNUM
    tnum=dataNUM(nn);
    fprintf(':: %d: processing (%d)\n', nn, tnum);
    if tnum<2
        continue;
    end
    fcsvPathINP=sprintf('%s/csv_by_numissl_%s/exp_%d.csv-path.txt', dirCFG,tptd,tnum);
    lstPathINP=textread(fcsvPathINP, '%s');
    lstPathINP={lstPathINP{2:end}};
    numFN=numel(lstPathINP);
    parfor ff=1:numFN
        tfn=lstPathINP{ff};
        [pathstr,name,ext] = fileparts(tfn);
        nameb=name(1:end-8);
        fnINP=sprintf('%s/%s', dirINP,tfn);
        fnOUT=sprintf('%s/%s_r%d.png', dirINP,tfn, nsiz(1));
        if exist(fnOUT,'file')~=2
           try
               timg=imread(fnINP);
               if ~ismatrix(timg)
                   timg=rgb2gray(timg);
               end
               timg=im2double(timg);
               timg=imadjust(timg);
% %                timg=255*(timg - min(timg(:)))/(max(timg(:)) - min(timg(:)));
               timgr=imresize(timg,nsiz);
               timgr8u=uint8(255*(timgr - min(timgr(:)))/(max(timgr(:)) - min(timgr(:))));
               imwrite(timgr8u,fnOUT);
% %                disp(size(timgr));
           catch
               strErr=sprintf('Error processing file (%s) --> (%s)\n', fnINP, fnOUT);
               t=getCurrentTask;
               foutLog='log.txt';
               if ~isempty(t)
                   foutLog=sprintf('log_%d.txt', t.ID);
               end
               f=fopen(foutLog, 'a');
               fprintf(f, strErr);
               fclose(f);
               fprintf('**** [ERROR] **** %s\n', strErr);
           end
        end
    end
end
