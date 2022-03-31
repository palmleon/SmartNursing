clear all
close all
clc
%% Library
import matlab.net.*
import matlab.net.http.*
%% Get request
r = RequestMessage;
uri = URI('https://api.thingspeak.com/channels.json?api_key=YTN43QRA4IWIEBIN');
resp = send(r,uri);
%% Retrive data
channel = resp.Body.Data(1);
data = thingSpeakRead(channel.id,'Fields',[1,2,3,4],NumPoints=8000,OutputFormat='matrix',ReadKey=channel.api_keys(2).api_key);
% remove NaN data
for col=1:width(data)
    i = 1;
    for row=1:height(data)
        if ~isnan(data(row,col))
            n_data(i,col) = data(row,col);
            i = i+1;
        end
    end
end
% temperature average (temperature is always in the first column)
temp_sum = 0;
count = 0;
for row=1:height(n_data)
    if n_data(row) >= 35
        temp_sum = temp_sum + n_data(row);
        count = count + 1;
    end
end
temp_avg = temp_sum/count
% avg saturation and pulse rate
sum_sat = 0;
sum_pulse = 0;
count = 0;
for row=1:height(n_data)
    if n_data(row,4) >= 4
        sum_sat = sum_sat + n_data(row,2);
        sum_pulse = sum_pulse + n_data(row,3);
        count = count + 1;
    end
end
avg_pulse = sum_pulse/count
avg_sat = sum_sat/count

