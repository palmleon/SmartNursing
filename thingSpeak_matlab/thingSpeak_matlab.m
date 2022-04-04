%% Library
import matlab.net.*
import matlab.net.http.*
%% API
mainAPI = "YTN43QRA4IWIEBIN";
%% Get request
r = RequestMessage;
uri = URI('https://api.thingspeak.com/channels.json?api_key=YTN43QRA4IWIEBIN');
resp = send(r,uri);
%% Retrive data, check and organise
len = length(resp.Body.Data);
for i=1:len
    channel = resp.Body.Data(i);
    data = thingSpeakRead(channel.id,'Fields',[2,3,4,6],NumPoints=8000,OutputFormat='timetable',ReadKey=channel.api_keys(2).api_key);
    perfusion_index = data(:,1).perfusionIndex;
    temperature = data(:,4).temperature;
    saturation = data(:,2).saturation;
    pulseRate = data(:,3).pulseRate;
return %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
end
% Remove NAN elements
    k=1;
    sum_index = 0;
    h = 1;
    for j=1:length(perfusion_index)
        if ~isnan(perfusion_index(j))
            if perfusion_index(j)>4
                n_perfusion_index(k) = perfusion_index(j);
                if ~isnan(saturation(j))
                sum_index = sum_index + n_perfusion_index(k);
                k = k+1;
            end
        end
    end
    avg_perfusion_index = sum/(k-1);
    k=1;
    sum = 0;
    for j=1:length(temperature)
        if ~isnan(temperature(j))
            if temperature(j)>35
                n_temperature(k) = temperature(j);
                sum = sum + n_temperature(k);
                k = k+1;
            end
        end
    end
    avg_temp(i) = sum/(k-1); 
end
return

%% Visualize Data %%
bar(10,2)
hold on
grid on
bar(1)
title("title")